from typing import Any


def write_report(
    answer: str,
    sql: str | None,
    evidence: list[str],
    verification: dict[str, Any],
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "answer": answer,
        "sql": sql,
        "evidence": evidence,
        "verification": verification,
        "limitations": limitations or [],
    }

