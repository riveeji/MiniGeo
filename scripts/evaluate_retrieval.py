from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.eval.retrieval import citation_hit_rate, mrr, recall_at_k
from minigeo.rag.corpus import load_corpus
from minigeo.rag.bm25 import BM25Retriever


def main() -> None:
    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    retriever = BM25Retriever(corpus)
    retrieved = {
        row["id"]: [item["chunk_id"] for item in retriever.search(row["question"], top_k=10)]
        for row in bench
    }
    print(f"retrieval_recall@5={recall_at_k(bench, retrieved, 5):.3f}")
    print(f"retrieval_recall@10={recall_at_k(bench, retrieved, 10):.3f}")
    print(f"mrr={mrr(bench, retrieved):.3f}")
    print(f"citation_hit_rate@10={citation_hit_rate(bench, retrieved):.3f}")


if __name__ == "__main__":
    main()

