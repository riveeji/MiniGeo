from typing import Any


def summarize_model_rag_outputs(
    benchmark_rows: list[dict[str, Any]],
    outputs: dict[str, dict[str, Any]],
    latency_ms: float | None = None,
) -> dict[str, Any]:
    if not benchmark_rows:
        return {
            "items": 0,
            "non_empty_answer_rate": 0.0,
            "citation_hit_rate": 0.0,
            "empty_raw_outputs": 0,
        }
    non_empty = 0
    citation_hits = 0
    empty_raw = 0
    for row in benchmark_rows:
        output = outputs.get(row["id"], {})
        answer = str(output.get("answer", "")).strip()
        raw = str(output.get("raw_model_output", "")).strip()
        citations = set(output.get("citations", []))
        gold = set(row.get("evidence", []))
        if answer:
            non_empty += 1
        if gold and citations.intersection(gold):
            citation_hits += 1
        if not raw:
            empty_raw += 1
    summary = {
        "items": len(benchmark_rows),
        "non_empty_answer_rate": non_empty / len(benchmark_rows),
        "citation_hit_rate": citation_hits / len(benchmark_rows),
        "empty_raw_outputs": empty_raw,
    }
    if latency_ms is not None:
        summary["latency_ms"] = latency_ms
    return summary
