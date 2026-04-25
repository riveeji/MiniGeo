from typing import Any


SQL_MARKERS = [
    "sql",
    "database",
    "schema",
    "样本",
    "地区",
    "预测",
    "误判",
    "错误",
    "多少",
    "统计",
    "表",
    "Qinhuangdao",
]

DOC_MARKERS = [
    "explain",
    "cause",
    "evidence",
    "spectral",
    "spectrum",
    "光谱",
    "证据",
    "原因",
    "成分",
    "矿物",
    "拉曼",
    "红外",
]


def _contains_any(text: str, markers: list[str]) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers)


def plan_agent_tools(question: str) -> dict[str, Any]:
    requires_sql = _contains_any(question, SQL_MARKERS)
    requires_docs = _contains_any(question, DOC_MARKERS)
    if requires_sql and requires_docs:
        mode = "hybrid"
    elif requires_sql:
        mode = "sql"
    else:
        requires_docs = True
        mode = "docs"
    return {
        "mode": mode,
        "requires_sql": requires_sql,
        "requires_docs": requires_docs,
        "requires_verification": True,
        "tools": _tools_for_mode(mode),
    }


def _tools_for_mode(mode: str) -> list[str]:
    if mode == "hybrid":
        return ["generate_sql", "execute_sql", "retrieve_evidence", "verify_answer", "write_report"]
    if mode == "sql":
        return ["generate_sql", "execute_sql", "verify_answer", "write_report"]
    return ["search_docs", "retrieve_evidence", "verify_answer", "write_report"]
