from minigeo.eval.retrieval_ablation import evaluate_retriever_outputs, run_retrieval_ablation
from minigeo.rag.dense import HashingEmbedder


def test_evaluate_retriever_outputs_returns_standard_metrics() -> None:
    gold = [{"id": "q1", "evidence": ["a"]}]
    retrieved = {"q1": ["b", "a"]}

    metrics = evaluate_retriever_outputs(gold, retrieved)

    assert metrics["recall@5"] == 1.0
    assert metrics["mrr"] == 0.5
    assert metrics["citation_hit_rate"] == 1.0


def test_run_retrieval_ablation_returns_all_systems() -> None:
    bench = [
        {
            "id": "q1",
            "question": "石英 二氧化硅",
            "evidence": ["quartz"],
        }
    ]
    corpus = [
        {"chunk_id": "quartz", "text": "石英 是 二氧化硅 矿物"},
        {"chunk_id": "calcite", "text": "方解石 是 碳酸盐 矿物"},
    ]

    results = run_retrieval_ablation(bench, corpus, top_k=2, embedder=HashingEmbedder(dimensions=64))

    assert set(results) == {"bm25", "dense", "hybrid", "hybrid_rerank"}
    assert results["hybrid"]["recall@5"] == 1.0
    assert results["bm25"]["latency_ms"] > 0.0
    assert results["hybrid_rerank"]["latency_ms"] > 0.0


def test_run_retrieval_ablation_accepts_custom_reranker() -> None:
    class ReverseReranker:
        def rerank(self, query, candidates, top_k=5):
            return list(reversed(candidates))[:top_k]

    bench = [{"id": "q1", "question": "石英", "evidence": ["calcite"]}]
    corpus = [
        {"chunk_id": "quartz", "text": "石英 二氧化硅"},
        {"chunk_id": "calcite", "text": "方解石 碳酸盐"},
    ]

    results = run_retrieval_ablation(
        bench,
        corpus,
        top_k=2,
        embedder=HashingEmbedder(dimensions=64),
        reranker=ReverseReranker(),
    )

    assert "hybrid_rerank" in results
