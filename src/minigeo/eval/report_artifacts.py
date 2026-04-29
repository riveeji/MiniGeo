from typing import Any


def _fmt(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _latency(metrics: dict[str, float]) -> str:
    value = metrics.get("latency_ms")
    if value is None:
        return "未测"
    return f"{value:.3f} ms/q"


def format_main_results(
    retrieval: dict[str, dict[str, float]],
    verifier: dict[str, Any],
    sql: dict[str, Any],
    abstention: dict[str, Any],
    agent_demo_passed: bool,
    planner: dict[str, Any] | None = None,
    agent_latency_ms: float | None = None,
    extra_rows: list[tuple[Any, ...]] | None = None,
) -> str:
    planner = planner or {}
    rows = [
        ("Qwen3.5-0.8B", "", "", "", "", "-", "未测"),
        ("Qwen3.5-2B", "", "", "", "", "-", "未测"),
        *(extra_rows or []),
        (
            "BM25 RAG baseline",
            "",
            retrieval.get("bm25", {}).get("citation_hit_rate"),
            "",
            abstention.get("abstention_accuracy"),
            "-",
            _latency(retrieval.get("bm25", {})),
        ),
        ("Dense baseline", "", retrieval.get("dense", {}).get("citation_hit_rate"), "", "", "-", _latency(retrieval.get("dense", {}))),
        ("Hybrid RAG baseline", "", retrieval.get("hybrid", {}).get("citation_hit_rate"), "", "", "-", _latency(retrieval.get("hybrid", {}))),
        (
            "Hybrid + rerank baseline",
            "",
            retrieval.get("hybrid_rerank", {}).get("citation_hit_rate"),
            "",
            "",
            "-",
            _latency(retrieval.get("hybrid_rerank", {})),
        ),
        ("Verifier baseline", "", "", verifier.get("unsupported_claim_rate"), "", "-", _latency(verifier)),
        ("SQL rule baseline", "", "", "", "", sql.get("sql_exec_accuracy"), _latency(sql)),
        ("Planner baseline", planner.get("sql_routing_accuracy"), "", "", "", "-", _latency(planner)),
        (
            "MiniGeo-Agent demo",
            "demo",
            "demo",
            "见 verifier",
            "demo",
            "PASS" if agent_demo_passed else "FAIL",
            "未测" if agent_latency_ms is None else f"{agent_latency_ms:.3f} ms/q",
        ),
    ]
    lines = [
        "# MiniGeo 主结果",
        "",
        "本表由 `scripts/write_report_artifacts.py` 生成，包含本地 baseline、demo 结果，以及已保存的真实模型服务结果。",
        "",
        "| System | Acc | Citation Hit | Unsupported Claim | Abstention | SQL Exec | Latency |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_fmt(value) for value in row) + " |")
    lines.extend(
        [
            "",
            "## 待补充模型结果",
            "",
            "- Qwen3.5-2B no-RAG。",
            "- Qwen3.5-2B + 模型 RAG。",
            "- MiniGeo-2B-SFT。",
            "- MiniGeo-2B-SFT + RAG + Verifier。",
            "- Qwen3.5-4B + RAG 的 300 题全量模型服务结果。",
            "",
        ]
    )
    return "\n".join(lines)


def format_failure_cases(cases: list[dict[str, Any]]) -> str:
    lines = [
        "# MiniGeo 失败案例",
        "",
        "本文件由 `scripts/write_report_artifacts.py` 生成，用于沉淀检索、Verifier、SQL 和 Agent 的可复查失败样例。",
        "",
    ]
    if not cases:
        lines.extend(["当前本地规则 baseline 未生成失败样例。", ""])
        return "\n".join(lines)
    for case in cases:
        lines.extend(
            [
                "```text",
                f"case_id: {case.get('case_id')}",
                f"question: {case.get('question')}",
                f"system: {case.get('system')}",
                f"observed_output: {case.get('observed_output')}",
                f"expected_behavior: {case.get('expected_behavior')}",
                f"failure_type: {case.get('failure_type')}",
                f"suspected_cause: {case.get('suspected_cause')}",
                f"next_action: {case.get('next_action')}",
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def abstention_failure_cases(
    benchmark_rows: list[dict[str, Any]],
    answers: dict[str, dict[str, Any]],
    max_cases: int = 5,
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for row in benchmark_rows:
        if row.get("answerable", True):
            continue
        answer = answers.get(row["id"], {})
        if answer.get("abstained") is True:
            continue
        cases.append(
            {
                "case_id": f"abstention_{len(cases) + 1:03d}",
                "question": row["question"],
                "system": "BM25 RAG baseline",
                "observed_output": ", ".join(answer.get("citations", [])) or str(answer),
                "expected_behavior": "应拒答并说明当前证据不足。",
                "failure_type": "missed_abstain",
                "suspected_cause": "检索到相关矿物或系统规则 chunk，但证据不足以回答题目中的特定样本或完整峰位要求。",
                "next_action": "增强问题意图识别，区分一般矿物知识与特定样本、完整峰表、资料库覆盖性问题。",
            }
        )
        if len(cases) >= max_cases:
            break
    return cases
