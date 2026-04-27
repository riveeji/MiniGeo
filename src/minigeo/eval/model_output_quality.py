from typing import Any


def analyze_model_outputs(records: list[dict[str, Any]], benchmark_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    benchmark_by_id = {str(row["id"]): row for row in benchmark_rows or []}
    items = len(records)
    citation_miss = 0
    thinking_answer = 0
    thinking_raw = 0
    placeholder_answer = 0
    format_errors = 0
    request_errors = 0
    abstention_errors = 0
    abstention_items = 0

    for record in records:
        result = record.get("result", {})
        answer = str(result.get("answer", "")).strip()
        raw = str(result.get("raw_model_output", "")).strip()
        citations = set(result.get("citations", []))
        gold = set(record.get("gold_evidence", []))
        if gold and not citations.intersection(gold):
            citation_miss += 1
        if _contains_thinking(answer):
            thinking_answer += 1
        if _contains_thinking(raw):
            thinking_raw += 1
        if answer.lower() in {"", "string"}:
            placeholder_answer += 1
        if result.get("format_error"):
            format_errors += 1
        if result.get("error"):
            request_errors += 1
        benchmark = benchmark_by_id.get(str(record.get("id")))
        if benchmark and "answerable" in benchmark:
            abstention_items += 1
            expected_abstain = not bool(benchmark.get("answerable", True))
            if bool(result.get("abstained", False)) != expected_abstain:
                abstention_errors += 1

    return {
        "items": items,
        "citation_miss_count": citation_miss,
        "citation_miss_rate": _rate(citation_miss, items),
        "thinking_answer_count": thinking_answer,
        "thinking_answer_rate": _rate(thinking_answer, items),
        "thinking_raw_count": thinking_raw,
        "thinking_raw_rate": _rate(thinking_raw, items),
        "placeholder_answer_count": placeholder_answer,
        "placeholder_answer_rate": _rate(placeholder_answer, items),
        "format_error_count": format_errors,
        "format_error_rate": _rate(format_errors, items),
        "request_errors": request_errors,
        "abstention_error_count": abstention_errors,
        "abstention_error_rate": _rate(abstention_errors, abstention_items),
    }


def format_model_output_quality_markdown(summaries: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# MiniGeo 模型输出质量审计",
        "",
        "本报告基于已保存的模型服务 JSONL 输出离线生成，不会再次调用模型。",
        "",
        "| Mode | Items | Citation Miss | Thinking Answer | Placeholder Answer | Format Error | Abstention Error | Request Errors |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for mode, summary in summaries.items():
        lines.append(
            "| "
            f"{mode} | "
            f"{summary['items']} | "
            f"{summary['citation_miss_rate']:.3f} | "
            f"{summary['thinking_answer_rate']:.3f} | "
            f"{summary['placeholder_answer_rate']:.3f} | "
            f"{summary.get('format_error_rate', 0.0):.3f} | "
            f"{summary['abstention_error_rate']:.3f} | "
            f"{summary['request_errors']} |"
        )
    lines.extend(
        [
            "",
            "## 解释",
            "",
            "- `Citation Miss`：answerable/evidence 题中，模型 citation 未命中 benchmark evidence。",
            "- `Thinking Answer`：最终 `answer` 字段仍包含 Thinking Process，说明输出格式未完全受控。",
            "- `Placeholder Answer`：模型输出了空答案或 `string` 这类 schema 占位文本。",
            "- `Format Error`：parser 明确判定该输出不满足最终 JSON contract。",
            "- `Abstention Error`：模型拒答行为与 benchmark 的 `answerable` 标签不一致。",
            "",
        ]
    )
    return "\n".join(lines)


def _contains_thinking(text: str) -> bool:
    lowered = text.lower()
    return "thinking process" in lowered or "<think>" in lowered


def _rate(count: int, total: int) -> float:
    return count / total if total else 0.0
