import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from minigeo.benchmark import load_benchmark
from minigeo.eval.model_service import summarize_model_rag_outputs
from minigeo.jsonl import read_jsonl, write_jsonl
from minigeo.llm.openai_compatible import client_from_env
from minigeo.rag.corpus import load_corpus
from minigeo.rag.model_rag import generate_model_rag_answer, parse_model_answer


def generate_no_rag_answer(question: str, client) -> dict[str, Any]:
    prompt = (
        "Answer the geoscience question from your own knowledge. "
        "Output only one JSON object. Do not output markdown, schema examples, or thinking process.\n"
        "The JSON keys must be answer, citations, abstained, confidence.\n"
        "The answer value must be the final Chinese answer, never the literal word string.\n"
        "Do not invent document citations. If you are unsure, set abstained to true.\n\n"
        f"Question: {question}"
    )
    raw = client.generate(prompt)
    parsed = parse_model_answer(raw, allowed_citations=set())
    parsed["evidence"] = []
    parsed["raw_model_output"] = raw
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a limited real model-service RAG smoke evaluation.")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--mode", choices=["rag", "no-rag", "both"], default="rag")
    parser.add_argument("--output", default="results/model_service_rag_smoke.jsonl")
    parser.add_argument("--no-resume", action="store_true", help="Ignore existing output files and start from scratch.")
    args = parser.parse_args()

    benchmark = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    rows = [row for row in benchmark if row.get("evidence")][: args.limit]
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    client = client_from_env()
    modes = ["rag", "no-rag"] if args.mode == "both" else [args.mode]
    summaries = {}
    output_paths = {}
    for mode in modes:
        output_path = _mode_output_path(Path(args.output), mode, len(modes) > 1)
        summaries[mode] = _run_mode(mode, rows, corpus, client, output_path, resume=not args.no_resume)
        output_paths[mode] = output_path
        print(json.dumps({"mode": mode, **summaries[mode]}, ensure_ascii=False))
        print(f"wrote={output_path}")
    Path("results/model_service_eval.md").write_text(
        _format_markdown(summaries, output_paths),
        encoding="utf-8",
        newline="\n",
    )
    print("wrote=results/model_service_eval.md")


def _mode_output_path(path: Path, mode: str, multi_mode: bool) -> Path:
    if not multi_mode:
        return path
    return path.with_name(f"{path.stem}_{mode.replace('-', '_')}{path.suffix}")


def _run_mode(
    mode: str,
    rows: list[dict[str, Any]],
    corpus: list[dict[str, Any]],
    client,
    output_path: Path,
    resume: bool = True,
) -> dict[str, Any]:
    outputs = {}
    records = _load_existing_records(output_path) if resume else []
    completed_ids = {str(record.get("id")) for record in records}
    for record in records:
        if "result" in record:
            outputs[str(record["id"])] = record["result"]
    started = perf_counter()
    for row in rows:
        if row["id"] in completed_ids:
            continue
        try:
            if mode == "rag":
                result = generate_model_rag_answer(row["question"], corpus, client, top_k=5)
            else:
                result = generate_no_rag_answer(row["question"], client)
        except Exception as exc:
            result = {
                "answer": "",
                "citations": [],
                "abstained": True,
                "confidence": 0.0,
                "evidence": [],
                "raw_model_output": "",
                "error": str(exc),
            }
        outputs[row["id"]] = result
        records.append(
            {
                "id": row["id"],
                "question": row["question"],
                "gold_evidence": row.get("evidence", []),
                "result": result,
            }
        )
        write_jsonl(output_path, records)
        print(json.dumps({"mode": mode, "id": row["id"], "error": result.get("error")}, ensure_ascii=False), flush=True)
    latency_ms = (perf_counter() - started) * 1000.0 / max(len(rows), 1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_path, records)
    return summarize_model_rag_outputs(rows, outputs, latency_ms=latency_ms)


def _load_existing_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return read_jsonl(path)


def _format_markdown(summaries: dict[str, dict[str, Any]], output_paths: dict[str, Path]) -> str:
    lines = [
        "# MiniGeo 模型服务评测",
        "",
        "本报告记录 OpenAI-compatible 模型服务的真实调用结果，用于补充主结果表。",
        "",
        "| Mode | Items | Non-empty | Citation Hit | Abstention Acc | Empty Raw | Request Errors | Latency | Raw Outputs |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for mode, summary in summaries.items():
        lines.append(
            "| "
            f"{mode} | "
            f"{summary['items']} | "
            f"{summary['non_empty_answer_rate']:.3f} | "
            f"{summary['citation_hit_rate']:.3f} | "
            f"{summary.get('abstention_accuracy', 0.0):.3f} | "
            f"{summary['empty_raw_outputs']} | "
            f"{summary.get('request_errors', 0)} | "
            f"{summary.get('latency_ms', 0.0):.3f} ms/q | "
            f"`{output_paths[mode]}` |"
        )
    lines.extend(
        [
            "",
            "## 本次外部模型服务",
            "",
            "- 服务形态：Colab A100 + vLLM OpenAI-compatible API + Cloudflare quick tunnel",
            "- 模型：`Qwen/Qwen3.5-4B`",
            "- `/v1/models` 连通性：通过",
            "",
            "说明：Cloudflare quick tunnel 和 Colab runtime 都是临时服务。若 Colab 页面停止、运行时断开或 tunnel cell 被中断，本地评测需要换成新的 tunnel URL 后重新运行。",
            "",
            "## 解释",
            "",
            "- `non_empty_answer_rate=0` 通常表示服务返回的 `message.content` 为空，或模型没有按 JSON contract 输出。",
            "- `citation_hit_rate` 统计模型返回 citation 与 benchmark evidence 的交集比例。",
            "- `no-rag` 模式不提供文档证据，因此 citation hit 通常应显著低于 RAG。",
            "- `empty_raw_outputs>0` 说明 MiniGeo 没有收到可解析的最终回答文本。",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
