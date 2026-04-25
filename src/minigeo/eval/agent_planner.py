from collections import Counter
from typing import Any

from minigeo.agent.planner import plan_agent_tools


def planner_sql_accuracy(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    correct = 0
    for row in rows:
        plan = plan_agent_tools(row["question"])
        if bool(plan["requires_sql"]) == bool(row.get("requires_sql", False)):
            correct += 1
    return correct / len(rows)


def summarize_planner_routes(rows: list[dict[str, Any]], latency_ms: float | None = None) -> dict[str, Any]:
    modes: Counter[str] = Counter()
    for row in rows:
        modes.update([plan_agent_tools(row["question"])["mode"]])
    summary: dict[str, Any] = {
        "items": len(rows),
        "sql_routing_accuracy": planner_sql_accuracy(rows),
        "modes": dict(modes),
    }
    if latency_ms is not None:
        summary["latency_ms"] = latency_ms
    return summary
