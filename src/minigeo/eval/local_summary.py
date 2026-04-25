from typing import Any


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def format_markdown_summary(
    benchmark: dict[str, Any],
    retrieval: dict[str, dict[str, float]],
    verifier: dict[str, Any],
    sql: dict[str, Any],
) -> str:
    lines = [
        "# MiniGeo 本地评测汇总",
        "",
        "本文件由 `scripts/write_local_results.py` 生成，记录当前本地 baseline 的可复现实验结果。",
        "",
        "## Benchmark",
        "",
        f"- 题目数：{benchmark.get('items')}",
        f"- SQL 题数：{benchmark.get('requires_sql')}",
        f"- 带 evidence label：{benchmark.get('evidence_labeled')}",
        "",
        "## Retrieval",
        "",
        "| 系统 | Recall@5 | Recall@10 | MRR | Citation Hit |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, metrics in retrieval.items():
        lines.append(
            f"| {name} | {_fmt(metrics.get('recall@5', 0.0))} | {_fmt(metrics.get('recall@10', 0.0))} | "
            f"{_fmt(metrics.get('mrr', 0.0))} | {_fmt(metrics.get('citation_hit_rate', 0.0))} |"
        )
    lines.extend(
        [
            "",
            "## Verifier",
            "",
            f"- reports：{verifier.get('reports')}",
            f"- claims：{verifier.get('claims')}",
            f"- unsupported_claim_rate：{_fmt(verifier.get('unsupported_claim_rate', 0.0))}",
            "",
            "## SQL",
            "",
            f"- sql_items：{sql.get('sql_items')}",
            f"- sql_exec_accuracy：{_fmt(sql.get('sql_exec_accuracy', 0.0))}",
            f"- failures：{sql.get('failures')}",
            "",
        ]
    )
    return "\n".join(lines)

