from typing import Any
from time import perf_counter

from minigeo.eval.retrieval import citation_hit_rate, mrr, recall_at_k
from minigeo.rag.bm25 import BM25Retriever
from minigeo.rag.dense import Embedder, DenseRetriever
from minigeo.rag.hybrid import hybrid_search
from minigeo.rag.reranker import LexicalReranker


def evaluate_retriever_outputs(gold_rows: list[dict[str, Any]], retrieved: dict[str, list[str]]) -> dict[str, float]:
    return {
        "recall@5": recall_at_k(gold_rows, retrieved, 5),
        "recall@10": recall_at_k(gold_rows, retrieved, 10),
        "mrr": mrr(gold_rows, retrieved),
        "citation_hit_rate": citation_hit_rate(gold_rows, retrieved),
    }


def _ids_by_query(rows: list[dict[str, Any]], retriever) -> tuple[dict[str, list[str]], float]:
    started = perf_counter()
    retrieved = {
        row["id"]: [item["chunk_id"] for item in retriever(row["question"])]
        for row in rows
    }
    elapsed_ms = (perf_counter() - started) * 1000.0
    latency_ms = elapsed_ms / max(len(rows), 1)
    return retrieved, max(latency_ms, 0.000001)


def run_retrieval_ablation(
    benchmark_rows: list[dict[str, Any]],
    corpus_rows: list[dict[str, Any]],
    top_k: int = 10,
    embedder: Embedder | None = None,
    reranker: Any | None = None,
) -> dict[str, dict[str, float]]:
    bm25 = BM25Retriever(corpus_rows)
    dense = DenseRetriever(corpus_rows, embedder=embedder)
    reranker = reranker or LexicalReranker()

    outputs = {}
    latencies = {}
    for name, retrieved, latency_ms in [
        (
            "bm25",
            *_ids_by_query(benchmark_rows, lambda query: bm25.search(query, top_k=top_k)),
        ),
        (
            "dense",
            *_ids_by_query(benchmark_rows, lambda query: dense.search(query, top_k=top_k)),
        ),
        (
            "hybrid",
            *_ids_by_query(
                benchmark_rows,
                lambda query: hybrid_search(query, corpus_rows, top_k=top_k, embedder=embedder),
            ),
        ),
        (
            "hybrid_rerank",
            *_ids_by_query(
                benchmark_rows,
                lambda query: reranker.rerank(
                    query,
                    hybrid_search(query, corpus_rows, top_k=max(top_k * 2, top_k), embedder=embedder),
                    top_k=top_k,
                ),
            ),
        ),
    ]:
        outputs[name] = retrieved
        latencies[name] = latency_ms
    results = {}
    for name, retrieved in outputs.items():
        metrics = evaluate_retriever_outputs(benchmark_rows, retrieved)
        metrics["latency_ms"] = latencies[name]
        results[name] = metrics
    return results
