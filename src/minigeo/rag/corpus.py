from collections import Counter
from pathlib import Path
from typing import Any

from minigeo.jsonl import read_jsonl

REQUIRED_CORPUS_FIELDS = {
    "chunk_id",
    "doc_id",
    "text",
    "source",
    "url",
    "page",
    "topic",
    "mineral",
    "license",
}


def validate_corpus_row(row: dict[str, Any]) -> None:
    missing = REQUIRED_CORPUS_FIELDS - row.keys()
    if missing:
        raise ValueError(f"Corpus row {row.get('chunk_id', '<unknown>')} missing fields: {sorted(missing)}")
    if not row["chunk_id"]:
        raise ValueError("chunk_id must not be empty")
    if not str(row["text"]).strip():
        raise ValueError(f"text must not be empty for {row['chunk_id']}")


def load_corpus(path: Path) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    seen: set[str] = set()
    for row in rows:
        validate_corpus_row(row)
        if row["chunk_id"] in seen:
            raise ValueError(f"Duplicate chunk_id: {row['chunk_id']}")
        seen.add(row["chunk_id"])
    return rows


def corpus_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    token_count = sum(len(str(row["text"]).split()) for row in rows)
    return {
        "chunks": len(rows),
        "topics": dict(Counter(row["topic"] for row in rows)),
        "minerals": dict(Counter(row["mineral"] for row in rows if row.get("mineral"))),
        "sources": dict(Counter(row["source"] for row in rows)),
        "approx_whitespace_tokens": token_count,
    }

