import argparse
from pathlib import Path
import sys

from minigeo.benchmark import load_benchmark
from minigeo.eval.retrieval_ablation import run_retrieval_ablation
from minigeo.rag.corpus import load_corpus
from minigeo.rag.embedding_service import embedding_embedder_from_env
from minigeo.rag.reranker_service import reranker_from_env


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate BM25, dense, hybrid, and hybrid+rerank retrieval.")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument(
        "--use-services",
        action="store_true",
        help="Use embedding/reranker services from environment variables instead of local baselines.",
    )
    args = parser.parse_args()

    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    try:
        embedder = embedding_embedder_from_env() if args.use_services else None
        reranker = reranker_from_env() if args.use_services else None
    except ValueError as exc:
        print(f"configuration_error={exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    results = run_retrieval_ablation(bench, corpus, top_k=args.top_k, embedder=embedder, reranker=reranker)
    for system, metrics in results.items():
        joined = " ".join(f"{key}={value:.3f}" for key, value in metrics.items())
        print(f"{system}: {joined}")


if __name__ == "__main__":
    main()
