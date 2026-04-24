from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.rag.corpus import load_corpus


def test_seed_benchmark_reaches_resume_ready_scale() -> None:
    rows = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))

    risk_items = [row for row in rows if row["type"] in {"unanswerable", "false_premise"}]
    sql_items = [row for row in rows if row["requires_sql"]]

    assert len(rows) >= 150
    assert len(risk_items) >= 30
    assert len(sql_items) >= 30


def test_seed_evidence_ids_exist_in_corpus() -> None:
    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    chunk_ids = {row["chunk_id"] for row in corpus}
    referenced = {
        evidence_id
        for row in bench
        for evidence_id in row["evidence"]
    }

    assert len(corpus) >= 30
    assert referenced <= chunk_ids

