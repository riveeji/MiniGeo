from typing import Any

from minigeo.finetune.sft import find_reference_answer_leaks
from minigeo.rag.corpus import REQUIRED_CORPUS_FIELDS


def audit_data_quality(
    benchmark_rows: list[dict[str, Any]],
    corpus_rows: list[dict[str, Any]],
    sft_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    chunk_ids = {row["chunk_id"] for row in corpus_rows}
    missing_evidence_refs = []
    for row in benchmark_rows:
        for chunk_id in row.get("evidence", []):
            if chunk_id not in chunk_ids:
                missing_evidence_refs.append(f"{row['id']}:{chunk_id}")

    metadata_missing = []
    optional_blank_fields = {"page", "mineral"}
    for row in corpus_rows:
        for field in REQUIRED_CORPUS_FIELDS:
            value = row.get(field)
            if field in optional_blank_fields:
                continue
            if value is None or value == "":
                metadata_missing.append(f"{row.get('chunk_id', '<unknown>')}:{field}")

    return {
        "benchmark_items": len(benchmark_rows),
        "corpus_chunks": len(corpus_rows),
        "sft_items": len(sft_rows),
        "missing_evidence_refs": missing_evidence_refs,
        "reference_answer_leaks": find_reference_answer_leaks(sft_rows, benchmark_rows),
        "metadata_missing": metadata_missing,
        "duplicate_chunk_ids": _duplicates([row["chunk_id"] for row in corpus_rows]),
        "duplicate_benchmark_ids": _duplicates([row["id"] for row in benchmark_rows]),
        "duplicate_sft_ids": _duplicates([row["id"] for row in sft_rows]),
    }


def _duplicates(values: list[str]) -> list[str]:
    seen = set()
    dupes = []
    for value in values:
        if value in seen and value not in dupes:
            dupes.append(value)
        seen.add(value)
    return dupes


def _list_or_ok(values: list[str]) -> str:
    if not values:
        return "OK"
    return "\n".join(f"- {value}" for value in values)


def format_data_quality_report(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# MiniGeo 数据质量审计",
            "",
            "本报告由 `scripts/audit_data_quality.py` 生成，用于检查 benchmark、RAG corpus 和 SFT 草案数据的基础质量。",
            "",
            "## 规模",
            "",
            f"- benchmark_items：{report['benchmark_items']}",
            f"- corpus_chunks：{report['corpus_chunks']}",
            f"- sft_items：{report['sft_items']}",
            "",
            "## Evidence 引用缺失",
            "",
            _list_or_ok(report["missing_evidence_refs"]),
            "",
            "## SFT 泄漏检查",
            "",
            _list_or_ok(report["reference_answer_leaks"]),
            "",
            "## Corpus Metadata 缺失",
            "",
            _list_or_ok(report["metadata_missing"]),
            "",
            "## 重复 ID",
            "",
            f"- duplicate_chunk_ids：{report.get('duplicate_chunk_ids') or 'OK'}",
            f"- duplicate_benchmark_ids：{report.get('duplicate_benchmark_ids') or 'OK'}",
            f"- duplicate_sft_ids：{report.get('duplicate_sft_ids') or 'OK'}",
            "",
        ]
    )
