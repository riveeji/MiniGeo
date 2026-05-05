from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from minigeo.agent.simple_agent import MiniGeoAgent


@dataclass(frozen=True)
class AgentCase:
    case_id: str
    question: str
    expected_mode: str
    requires_sql: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "question": self.question,
            "expected_mode": self.expected_mode,
            "requires_sql": self.requires_sql,
        }


DEFAULT_AGENT_CASES = [
    AgentCase(
        case_id="agent_hybrid_qhd_misclassification",
        question=(
            "Analyze which mineral categories are most frequently misclassified in samples collected from Qinhuangdao, "
            "and explain possible causes using spectral evidence."
        ),
        expected_mode="hybrid",
        requires_sql=True,
    ).to_dict(),
    AgentCase(
        case_id="agent_sql_region_errors",
        question="每个地区有多少错误预测？",
        expected_mode="sql",
        requires_sql=True,
    ).to_dict(),
    AgentCase(
        case_id="agent_docs_quartz_spectrum",
        question="石英的主要拉曼光谱证据是什么？",
        expected_mode="docs",
        requires_sql=False,
    ).to_dict(),
]


def evaluate_agent_cases(
    cases: list[dict[str, Any]],
    db_path: Path,
    corpus: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    agent = MiniGeoAgent(db_path=db_path, corpus=corpus)
    reports: list[dict[str, Any]] = []
    started = perf_counter()
    for case in cases:
        reports.append(_evaluate_one_case(agent, case))
    latency_ms = (perf_counter() - started) * 1000.0 / max(len(cases), 1)
    summary = _summarize(reports, latency_ms=latency_ms)
    return summary, reports


def _evaluate_one_case(agent: MiniGeoAgent, case: dict[str, Any]) -> dict[str, Any]:
    try:
        report = agent.run(str(case["question"]))
        error = None
    except Exception as exc:  # pragma: no cover - guarded result for audit CLI
        report = {}
        error = f"{type(exc).__name__}: {exc}"

    actual_mode = report.get("plan", {}).get("mode")
    sql_error = report.get("sql_result", {}).get("error")
    verification = report.get("verification", {})
    expected_mode = str(case["expected_mode"])
    requires_sql = bool(case["requires_sql"])
    checks = {
        "plan_mode": actual_mode == expected_mode,
        "sql_success": (not requires_sql) or (bool(report.get("sql")) and sql_error is None),
        "answer_present": bool(report.get("answer")),
        "evidence_present": bool(report.get("evidence")),
        "verification_present": bool(verification.get("verdict")),
        "limitations_present": bool(report.get("limitations")),
        "no_exception": error is None,
    }
    passed = all(checks.values())
    return {
        "case_id": case["case_id"],
        "question": case["question"],
        "expected_mode": expected_mode,
        "requires_sql": requires_sql,
        "actual_mode": actual_mode,
        "passed": passed,
        "checks": checks,
        "answer": report.get("answer", ""),
        "sql": report.get("sql"),
        "sql_error": sql_error,
        "evidence": report.get("evidence", []),
        "verification_verdict": verification.get("verdict"),
        "error": error,
    }


def _summarize(reports: list[dict[str, Any]], latency_ms: float) -> dict[str, Any]:
    total = max(len(reports), 1)
    sql_reports = [report for report in reports if report["requires_sql"]]
    return {
        "items": len(reports),
        "pass_rate": _rate(reports, lambda report: bool(report["passed"]), total),
        "plan_mode_accuracy": _rate(reports, lambda report: report["actual_mode"] == report["expected_mode"], total),
        "sql_success_rate": _rate(sql_reports, lambda report: report["sql_error"] is None, max(len(sql_reports), 1)),
        "verification_report_rate": _rate(
            reports,
            lambda report: bool(report["verification_verdict"]),
            total,
        ),
        "evidence_rate": _rate(reports, lambda report: bool(report["evidence"]), total),
        "latency_ms": round(latency_ms, 3),
    }


def _rate(rows: list[dict[str, Any]], predicate: Any, denominator: int) -> float:
    return round(sum(1 for row in rows if predicate(row)) / denominator, 4)


def format_agent_case_report(summary: dict[str, Any], reports: list[dict[str, Any]]) -> str:
    lines = [
        "# MiniGeo-Agent 多案例本地评测",
        "",
        "## 摘要",
        "",
        f"- 样例数：{summary['items']}",
        f"- 通过率：{summary['pass_rate']:.2%}",
        f"- Planner 模式准确率：{summary['plan_mode_accuracy']:.2%}",
        f"- SQL 成功率：{summary['sql_success_rate']:.2%}",
        f"- Verification report 覆盖率：{summary['verification_report_rate']:.2%}",
        f"- 平均延迟：{summary['latency_ms']} ms/case",
        "",
        "## 案例明细",
        "",
        "| case_id | 期望模式 | 实际模式 | 通过 | SQL 错误 | Evidence | Verdict |",
        "|---|---|---|---:|---|---:|---|",
    ]
    for report in reports:
        sql_error = report["sql_error"] or report["error"] or ""
        lines.append(
            "| {case_id} | {expected_mode} | {actual_mode} | {passed} | {sql_error} | {evidence_count} | {verdict} |".format(
                case_id=report["case_id"],
                expected_mode=report["expected_mode"],
                actual_mode=report["actual_mode"],
                passed="是" if report["passed"] else "否",
                sql_error=sql_error.replace("|", "\\|"),
                evidence_count=len(report["evidence"]),
                verdict=report["verification_verdict"] or "",
            )
        )
    lines.extend(["", "## 问题与回答", ""])
    for report in reports:
        lines.extend(
            [
                f"### {report['case_id']}",
                "",
                f"- 问题：{report['question']}",
                f"- 回答：{report['answer']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
