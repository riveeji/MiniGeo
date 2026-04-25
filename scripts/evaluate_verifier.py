import argparse
import os
from pathlib import Path
import sys
from time import perf_counter

from minigeo.benchmark import load_benchmark
from minigeo.eval.verifier import summarize_verification_reports
from minigeo.rag.corpus import load_corpus
from minigeo.verifier.factory import build_verifier_from_env


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate MiniGeo verifier on benchmark reference answers.")
    parser.add_argument("--use-model", action="store_true", help="Use model-backed claim extraction and support classification.")
    args = parser.parse_args()

    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    chunks_by_id = {row["chunk_id"]: row for row in corpus}
    env = dict(os.environ)
    if args.use_model:
        env["MINIGEO_VERIFIER_USE_MODEL"] = "1"
    try:
        verifier = build_verifier_from_env(env)
    except ValueError as exc:
        print(f"configuration_error={exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    reports = []
    started = perf_counter()
    for row in bench:
        evidence = [chunks_by_id[chunk_id] for chunk_id in row["evidence"] if chunk_id in chunks_by_id]
        reports.append(verifier.verify(row["answer"], evidence))
    latency_ms = (perf_counter() - started) * 1000.0 / max(len(bench), 1)
    summary = summarize_verification_reports(reports, latency_ms=latency_ms)
    for key, value in summary.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
