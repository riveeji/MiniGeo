from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.eval.verifier import summarize_verification_reports
from minigeo.rag.corpus import load_corpus
from minigeo.verifier.verifier import MiniGeoVerifier


def main() -> None:
    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    chunks_by_id = {row["chunk_id"]: row for row in corpus}
    verifier = MiniGeoVerifier()
    reports = []
    for row in bench:
        evidence = [chunks_by_id[chunk_id] for chunk_id in row["evidence"] if chunk_id in chunks_by_id]
        reports.append(verifier.verify(row["answer"], evidence))
    summary = summarize_verification_reports(reports)
    for key, value in summary.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()

