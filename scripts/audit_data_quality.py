from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.eval.data_quality import audit_data_quality, format_data_quality_report
from minigeo.jsonl import read_jsonl
from minigeo.rag.corpus import load_corpus


def main() -> None:
    benchmark = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    sft = read_jsonl(Path("data/processed/sft_corpus.jsonl"))
    report = audit_data_quality(benchmark, corpus, sft)
    output = Path("results/data_quality.md")
    output.write_text(format_data_quality_report(report), encoding="utf-8", newline="\n")
    for key, value in report.items():
        print(f"{key}={value}")
    if any(
        report[key]
        for key in [
            "missing_evidence_refs",
            "reference_answer_leaks",
            "metadata_missing",
            "duplicate_chunk_ids",
            "duplicate_benchmark_ids",
            "duplicate_sft_ids",
        ]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
