import argparse
import json
import os
from pathlib import Path
import sys

from minigeo.benchmark import load_benchmark
from minigeo.eval.verified_model_service import (
    format_verified_model_report,
    summarize_verified_model_records,
    verify_saved_model_records,
)
from minigeo.jsonl import read_jsonl, write_jsonl
from minigeo.verifier.factory import build_verifier_from_env


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Verifier on saved model-service RAG outputs.")
    parser.add_argument("--benchmark", default="data/benchmark/minigeo_bench.jsonl")
    parser.add_argument("--input", default="results/model_service_qwen35_4b_150_rag.jsonl")
    parser.add_argument("--output", default="results/model_service_qwen35_4b_150_rag_verified.jsonl")
    parser.add_argument("--report", default="results/model_service_verified_eval_150.md")
    parser.add_argument("--use-model", action="store_true", help="Use model-backed verifier from env.")
    args = parser.parse_args()

    env = dict(os.environ)
    if args.use_model:
        env["MINIGEO_VERIFIER_USE_MODEL"] = "1"
    try:
        verifier = build_verifier_from_env(env)
    except ValueError as exc:
        print(f"configuration_error={exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    records = read_jsonl(Path(args.input))
    verified_records = verify_saved_model_records(records, verifier=verifier)
    output = Path(args.output)
    write_jsonl(output, verified_records)

    benchmark = load_benchmark(Path(args.benchmark))
    benchmark_by_id = {row["id"]: row for row in benchmark}
    matched_benchmark = [benchmark_by_id[record["id"]] for record in verified_records if record["id"] in benchmark_by_id]
    summary = summarize_verified_model_records(matched_benchmark, verified_records)

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        format_verified_model_report(
            summary["model"],
            summary["verifier"],
            str(output),
            verifier_mode="model" if args.use_model else "heuristic",
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, ensure_ascii=False))
    print(f"wrote={output}")
    print(f"wrote={report}")


if __name__ == "__main__":
    main()
