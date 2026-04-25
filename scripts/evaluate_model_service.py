import argparse
import json
from pathlib import Path
from time import perf_counter

from minigeo.benchmark import load_benchmark
from minigeo.eval.model_service import summarize_model_rag_outputs
from minigeo.jsonl import write_jsonl
from minigeo.llm.openai_compatible import client_from_env
from minigeo.rag.corpus import load_corpus
from minigeo.rag.model_rag import generate_model_rag_answer


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a limited real model-service RAG smoke evaluation.")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--output", default="results/model_service_rag_smoke.jsonl")
    args = parser.parse_args()

    benchmark = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    rows = [row for row in benchmark if row.get("evidence")][: args.limit]
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    client = client_from_env()
    outputs = {}
    records = []
    started = perf_counter()
    for row in rows:
        result = generate_model_rag_answer(row["question"], corpus, client, top_k=5)
        outputs[row["id"]] = result
        records.append(
            {
                "id": row["id"],
                "question": row["question"],
                "gold_evidence": row.get("evidence", []),
                "result": result,
            }
        )
    latency_ms = (perf_counter() - started) * 1000.0 / max(len(rows), 1)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_path, records)
    summary = summarize_model_rag_outputs(rows, outputs, latency_ms=latency_ms)
    Path("results/model_service_eval.md").write_text(
        _format_markdown(summary, output_path),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, ensure_ascii=False))
    print(f"wrote={output_path}")
    print("wrote=results/model_service_eval.md")


def _format_markdown(summary: dict, output_path: Path) -> str:
    return "\n".join(
        [
            "# MiniGeo 模型服务 Smoke Eval",
            "",
            "本报告记录 OpenAI-compatible 模型服务的小样本 RAG 评测结果。",
            "该脚本默认只跑少量样本，用于验证服务连通性、响应格式和引用行为，不替代完整 benchmark。",
            "",
            f"- items：{summary['items']}",
            f"- non_empty_answer_rate：{summary['non_empty_answer_rate']:.3f}",
            f"- citation_hit_rate：{summary['citation_hit_rate']:.3f}",
            f"- empty_raw_outputs：{summary['empty_raw_outputs']}",
            f"- latency_ms：{summary.get('latency_ms', 0.0):.3f}",
            f"- raw_outputs：`{output_path}`",
            "",
            "## 解释",
            "",
            "- `non_empty_answer_rate=0` 通常表示服务返回的 `message.content` 为空，或模型没有按 JSON contract 输出。",
            "- `empty_raw_outputs>0` 说明 MiniGeo 没有收到可解析的最终回答文本。",
            "- Ollama 的部分 thinking 模型可能把内容放入 `reasoning/thinking` 字段；MiniGeo 的 OpenAI-compatible 评测要求最终答案进入 `message.content`。",
            "",
        ]
    )


if __name__ == "__main__":
    main()
