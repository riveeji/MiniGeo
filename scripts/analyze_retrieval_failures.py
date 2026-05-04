import argparse
import csv
from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.eval.retrieval_failure_analysis import (
    analyze_retrieval_failures,
    collect_retrieval_outputs,
    format_retrieval_failure_report,
)
from minigeo.rag.corpus import load_corpus


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze retrieval miss cases by system and suspected cause.")
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark/minigeo_bench.jsonl"))
    parser.add_argument("--corpus", type=Path, default=Path("data/processed/rag_corpus.jsonl"))
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--markdown-output", type=Path, default=Path("results/retrieval_failure_analysis.md"))
    parser.add_argument("--csv-output", type=Path, default=Path("results/retrieval_failure_analysis.csv"))
    args = parser.parse_args()

    benchmark = load_benchmark(args.benchmark)
    corpus = load_corpus(args.corpus)
    outputs = collect_retrieval_outputs(benchmark, corpus, top_k=args.top_k)
    report = analyze_retrieval_failures(benchmark, corpus, outputs, top_k=args.top_k)

    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(format_retrieval_failure_report(report), encoding="utf-8", newline="\n")
    _write_cases_csv(args.csv_output, report["cases"])
    print(f"wrote={args.markdown_output}")
    print(f"wrote={args.csv_output}")


def _write_cases_csv(path: Path, cases: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "system",
        "id",
        "question",
        "expected_evidence",
        "retrieved_ids",
        "category",
        "suspected_cause",
        "next_action",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            writer.writerow(
                {
                    **case,
                    "expected_evidence": ";".join(case["expected_evidence"]),
                    "retrieved_ids": ";".join(case["retrieved_ids"]),
                }
            )


if __name__ == "__main__":
    main()
