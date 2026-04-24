from collections.abc import Iterable
from typing import Any


def _gold_ids(row: dict[str, Any]) -> set[str]:
    return set(row.get("evidence") or [])


def _evidence_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if _gold_ids(row)]


def recall_at_k(gold_rows: list[dict[str, Any]], retrieved: dict[str, list[str]], k: int) -> float:
    rows = _evidence_rows(gold_rows)
    if not rows:
        return 0.0
    hits = 0
    for row in rows:
        if _gold_ids(row) & set(retrieved.get(row["id"], [])[:k]):
            hits += 1
    return hits / len(rows)


def mrr(gold_rows: list[dict[str, Any]], retrieved: dict[str, list[str]]) -> float:
    rows = _evidence_rows(gold_rows)
    if not rows:
        return 0.0
    total = 0.0
    for row in rows:
        gold = _gold_ids(row)
        for rank, chunk_id in enumerate(retrieved.get(row["id"], []), start=1):
            if chunk_id in gold:
                total += 1 / rank
                break
    return total / len(rows)


def citation_hit_rate(gold_rows: list[dict[str, Any]], citations: dict[str, list[str]]) -> float:
    rows = _evidence_rows(gold_rows)
    if not rows:
        return 0.0
    hits = 0
    for row in rows:
        if _gold_ids(row) & set(citations.get(row["id"], [])):
            hits += 1
    return hits / len(rows)

