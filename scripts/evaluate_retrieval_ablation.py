from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.eval.retrieval_ablation import run_retrieval_ablation
from minigeo.rag.corpus import load_corpus


def main() -> None:
    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    results = run_retrieval_ablation(bench, corpus, top_k=10)
    for system, metrics in results.items():
        joined = " ".join(f"{key}={value:.3f}" for key, value in metrics.items())
        print(f"{system}: {joined}")


if __name__ == "__main__":
    main()

