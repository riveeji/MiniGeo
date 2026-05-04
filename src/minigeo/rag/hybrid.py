from typing import Any

from minigeo.rag.bm25 import BM25Retriever
from minigeo.rag.dense import Embedder, DenseRetriever


def _rank_score(rank: int) -> float:
    return 1.0 / (rank + 1)


def merge_ranked_results(
    bm25_results: list[dict[str, Any]],
    dense_results: list[dict[str, Any]],
    top_k: int = 5,
    bm25_weight: float = 0.5,
    dense_weight: float = 0.5,
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for rank, row in enumerate(bm25_results):
        chunk_id = row["chunk_id"]
        item = dict(row)
        item["bm25_rank_score"] = _rank_score(rank)
        item["dense_rank_score"] = 0.0
        merged[chunk_id] = item
    for rank, row in enumerate(dense_results):
        chunk_id = row["chunk_id"]
        item = merged.get(chunk_id, dict(row))
        item.setdefault("bm25_rank_score", 0.0)
        item["dense_rank_score"] = _rank_score(rank)
        if "dense_score" in row:
            item["dense_score"] = row["dense_score"]
        merged[chunk_id] = item
    for item in merged.values():
        item["hybrid_score"] = (
            bm25_weight * item.get("bm25_rank_score", 0.0)
            + dense_weight * item.get("dense_rank_score", 0.0)
        )
    return sorted(merged.values(), key=lambda item: item["hybrid_score"], reverse=True)[:top_k]


def hybrid_search(
    query: str,
    docs: list[dict[str, Any]],
    top_k: int = 5,
    candidate_k: int | None = None,
    embedder: Embedder | None = None,
    bm25_retriever: BM25Retriever | None = None,
    dense_retriever: DenseRetriever | None = None,
) -> list[dict[str, Any]]:
    candidate_k = candidate_k or max(top_k * 3, top_k)
    bm25 = bm25_retriever or BM25Retriever(docs)
    dense = dense_retriever or DenseRetriever(docs, embedder=embedder)
    bm25_results = bm25.search(query, top_k=candidate_k)
    dense_results = dense.search(query, top_k=candidate_k)
    return merge_ranked_results(bm25_results, dense_results, top_k=top_k)
