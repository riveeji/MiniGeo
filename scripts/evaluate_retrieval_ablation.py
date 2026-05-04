import argparse
from datetime import date as current_date
import json
import os
from pathlib import Path
import sys
from typing import Any

from minigeo.benchmark import load_benchmark
from minigeo.eval.retrieval_ablation import run_retrieval_ablation
from minigeo.rag.corpus import load_corpus
from minigeo.rag.embedding_service import embedding_embedder_from_env
from minigeo.rag.reranker_service import reranker_from_env


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate BM25, dense, hybrid, and hybrid+rerank retrieval.")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument(
        "--use-services",
        action="store_true",
        help="Use both embedding and reranker services from environment variables instead of local baselines.",
    )
    parser.add_argument(
        "--use-embedding-service",
        action="store_true",
        help="Use only the embedding service from environment variables; keep the local lexical reranker.",
    )
    parser.add_argument(
        "--use-reranker-service",
        action="store_true",
        help="Use only the reranker service from environment variables; keep the local hashing embedder.",
    )
    parser.add_argument("--json-output", type=Path, help="Optional path for a machine-readable service report.")
    parser.add_argument("--markdown-output", type=Path, help="Optional path for a Markdown service report.")
    args = parser.parse_args()

    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    use_embedding_service, use_reranker_service = _service_usage(
        args.use_services,
        args.use_embedding_service,
        args.use_reranker_service,
    )
    try:
        embedder = embedding_embedder_from_env() if use_embedding_service else None
        reranker = reranker_from_env() if use_reranker_service else None
    except ValueError as exc:
        print(f"configuration_error={exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    results = run_retrieval_ablation(bench, corpus, top_k=args.top_k, embedder=embedder, reranker=reranker)
    for system, metrics in results.items():
        joined = " ".join(f"{key}={value:.3f}" for key, value in metrics.items())
        print(f"{system}: {joined}")
    if args.json_output or args.markdown_output:
        mode = _service_mode(use_embedding_service, use_reranker_service)
        report = _build_service_report(
            metrics=results,
            mode=mode,
            embedding_model=os.environ.get("MINIGEO_EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B"),
            reranker_model=os.environ.get("MINIGEO_RERANKER_MODEL", "Qwen/Qwen3-Reranker-0.6B"),
            command="python " + " ".join(sys.argv),
        )
        if args.json_output:
            args.json_output.parent.mkdir(parents=True, exist_ok=True)
            args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
            print(f"wrote={args.json_output}")
        if args.markdown_output:
            args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
            args.markdown_output.write_text(_format_service_report(report), encoding="utf-8", newline="\n")
            print(f"wrote={args.markdown_output}")


def _service_usage(
    use_services: bool,
    use_embedding_service: bool,
    use_reranker_service: bool,
) -> tuple[bool, bool]:
    return (
        use_services or use_embedding_service,
        use_services or use_reranker_service,
    )


def _service_mode(use_embedding_service: bool, use_reranker_service: bool) -> str:
    if use_embedding_service and use_reranker_service:
        return "embedding_reranker_services"
    if use_embedding_service:
        return "embedding_service"
    if use_reranker_service:
        return "reranker_service"
    return "local"


def _short_model_name(model: str) -> str:
    return model.rstrip("/").split("/")[-1]


def _build_service_report(
    metrics: dict[str, dict[str, float]],
    mode: str,
    embedding_model: str,
    reranker_model: str,
    command: str,
    run_date: str | None = None,
) -> dict[str, Any]:
    report_date = run_date or str(current_date.today())
    embedding_short = _short_model_name(embedding_model)
    reranker_short = _short_model_name(reranker_model)
    main_rows: list[dict[str, Any]] = []
    if mode in {"embedding_service", "embedding_reranker_services"}:
        labels = {
            "dense": f"{embedding_short} dense retrieval",
            "hybrid": f"{embedding_short} hybrid retrieval",
            "hybrid_rerank": (
                f"{embedding_short} + {reranker_short} hybrid rerank"
                if mode == "embedding_reranker_services"
                else f"{embedding_short} hybrid + lexical rerank"
            ),
        }
    elif mode == "reranker_service":
        labels = {"hybrid_rerank": f"{reranker_short} hybrid rerank"}
    else:
        labels = {}
    for key, label in labels.items():
        if key not in metrics:
            continue
        main_rows.append(
            {
                "system": label,
                "citation_hit_rate": metrics[key].get("citation_hit_rate"),
                "latency": "见 retrieval_service_eval",
            }
        )
    return {
        "date": report_date,
        "service": "OpenAI-compatible retrieval service",
        "mode": mode,
        "embedding_model": embedding_model,
        "reranker_model": reranker_model,
        "command": command,
        "main_result_rows": main_rows,
        "metrics": metrics,
    }


def _format_value(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.3f}"


def _format_service_report(report: dict[str, Any]) -> str:
    lines = [
        "# MiniGeo 真实检索服务消融",
        "",
        "本报告记录真实 OpenAI-compatible 检索服务的调用结果，用于补充本地 deterministic baseline。",
        "",
        "## 本次服务",
        "",
        f"- 日期：{report['date']}",
        f"- 模式：`{report['mode']}`",
        f"- Embedding 模型：`{report['embedding_model']}`",
        f"- Reranker 模型：`{report['reranker_model']}`",
        f"- 命令：`{report['command']}`",
        "",
        "## 结果",
        "",
        "| System | Recall@5 | Recall@10 | MRR | Citation Hit | Latency |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    metrics = report["metrics"]
    for row in report["main_result_rows"]:
        system = row["system"]
        if "dense retrieval" in system:
            metric = metrics.get("dense", {})
        elif "hybrid rerank" in system or "lexical rerank" in system:
            metric = metrics.get("hybrid_rerank", {})
        else:
            metric = metrics.get("hybrid", {})
        lines.append(
            "| "
            + " | ".join(
                [
                    system,
                    _format_value(metric.get("recall@5")),
                    _format_value(metric.get("recall@10")),
                    _format_value(metric.get("mrr")),
                    _format_value(metric.get("citation_hit_rate")),
                    "" if metric.get("latency_ms") is None else f"{metric['latency_ms']:.3f} ms/q",
                ]
            )
            + " |"
        )
    lines.extend(["", "## 解释", ""])
    if report["mode"] == "embedding_service":
        lines.extend(
            [
                "- 本轮只接入真实 embedding 服务，reranker 仍为本地 lexical reranker。",
                "- Hybrid 的延迟可能受 embedding 缓存影响，正式延迟结论应单独做 cold/warm latency 评测。",
            ]
        )
    elif report["mode"] == "reranker_service":
        lines.append("- 本轮只接入真实 reranker 服务，dense embedding 仍为本地 deterministic baseline。")
    elif report["mode"] == "embedding_reranker_services":
        lines.append("- 本轮同时接入真实 embedding 和 reranker 服务，可作为完整检索服务消融结果。")
    else:
        lines.append("- 本轮未接入外部检索服务。")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
