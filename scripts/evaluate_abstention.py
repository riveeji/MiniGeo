from pathlib import Path
from time import perf_counter

from minigeo.benchmark import load_benchmark
from minigeo.eval.abstention import summarize_abstention
from minigeo.rag.corpus import load_corpus
from minigeo.rag.pipeline import offline_rag_answer


def main() -> None:
    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    started = perf_counter()
    answers = {row["id"]: offline_rag_answer(row["question"], corpus, top_k=3) for row in bench}
    latency_ms = (perf_counter() - started) * 1000.0 / max(len(bench), 1)
    summary = summarize_abstention(bench, answers, latency_ms=latency_ms)
    for key, value in summary.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
