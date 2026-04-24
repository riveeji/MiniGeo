from collections import Counter
from pathlib import Path
from typing import Any

from minigeo.jsonl import read_jsonl

REQUIRED_FIELDS = {
    "id",
    "question",
    "answer",
    "type",
    "difficulty",
    "answerable",
    "requires_sql",
    "evidence",
    "expected_sql_intent",
    "expected_result",
}

VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def validate_benchmark_item(row: dict[str, Any]) -> None:
    missing = REQUIRED_FIELDS - row.keys()
    if missing:
        raise ValueError(f"Benchmark item {row.get('id', '<unknown>')} missing fields: {sorted(missing)}")
    if row["difficulty"] not in VALID_DIFFICULTIES:
        raise ValueError(f"Invalid difficulty for {row['id']}: {row['difficulty']}")
    if not isinstance(row["answerable"], bool):
        raise ValueError(f"answerable must be bool for {row['id']}")
    if not isinstance(row["requires_sql"], bool):
        raise ValueError(f"requires_sql must be bool for {row['id']}")
    if not isinstance(row["evidence"], list):
        raise ValueError(f"evidence must be list for {row['id']}")


def load_benchmark(path: Path) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    seen: set[str] = set()
    for row in rows:
        validate_benchmark_item(row)
        if row["id"] in seen:
            raise ValueError(f"Duplicate benchmark id: {row['id']}")
        seen.add(row["id"])
    return rows


def benchmark_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    answerable = sum(1 for row in rows if row["answerable"])
    sql = sum(1 for row in rows if row["requires_sql"])
    evidence_labeled = sum(1 for row in rows if row["evidence"])
    return {
        "items": len(rows),
        "types": dict(Counter(row["type"] for row in rows)),
        "difficulty": dict(Counter(row["difficulty"] for row in rows)),
        "answerable": answerable,
        "unanswerable": len(rows) - answerable,
        "requires_sql": sql,
        "evidence_labeled": evidence_labeled,
    }

