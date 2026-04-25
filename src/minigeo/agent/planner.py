from typing import Any


SQL_MARKERS = [
    "sql",
    "database",
    "schema",
    "地区",
    "错误",
    "多少",
    "统计",
    "表",
    "查询",
    "记录",
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
    requires_sql = _requires_sql(question)
    requires_docs = _requires_docs(question, requires_sql)
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


def _requires_sql(question: str) -> bool:
    lowered = question.lower()
    if question.startswith("为什么") and not _contains_any(question, ["误判", "错误预测", "预测错误", "秦皇岛", "Qinhuangdao"]):
        return False
    if "misclassified" in lowered and "qinhuangdao" in lowered:
        return True
    if _contains_any(question, ["查询", "列出", "统计", "sql", "database", "schema"]):
        return True
    if "每个" in question and _contains_any(question, ["地区", "类别", "样本", "峰位"]):
        return True
    if _contains_any(question, ["误判", "错误预测", "预测错误", "预测类别"]) and _contains_any(question, ["Qinhuangdao", "秦皇岛", "地区", "多少"]):
        return True
    if "预测" in question and "错误" in question and _contains_any(question, ["Qinhuangdao", "秦皇岛", "sample_id"]):
        return True
    if "资料库" in question and "数据库记录" in question:
        return True
    if "表" in question and _contains_any(question, ["哪个", "哪些", "结构化字段"]):
        return True
    return False


def _requires_docs(question: str, requires_sql: bool) -> bool:
    if requires_sql and question.strip().startswith("查询"):
        return _contains_any(question, ["原因", "解释", "证据", "explain", "cause", "evidence"])
    return _contains_any(question, DOC_MARKERS)


def _tools_for_mode(mode: str) -> list[str]:
    if mode == "hybrid":
        return ["generate_sql", "execute_sql", "retrieve_evidence", "verify_answer", "write_report"]
    if mode == "sql":
        return ["generate_sql", "execute_sql", "verify_answer", "write_report"]
    return ["search_docs", "retrieve_evidence", "verify_answer", "write_report"]
