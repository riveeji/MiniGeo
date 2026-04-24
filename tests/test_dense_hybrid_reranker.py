from minigeo.rag.dense import DenseRetriever, HashingEmbedder, cosine_similarity
from minigeo.rag.hybrid import hybrid_search, merge_ranked_results
from minigeo.rag.reranker import LexicalReranker


def test_hashing_embedder_is_deterministic_and_similarity_is_normalized() -> None:
    embedder = HashingEmbedder(dimensions=32)

    first = embedder.embed("石英 二氧化硅")
    second = embedder.embed("石英 二氧化硅")
    unrelated = embedder.embed("方解石 碳酸盐")

    assert first == second
    assert cosine_similarity(first, first) == 1.0
    assert cosine_similarity(first, unrelated) < 1.0


def test_dense_retriever_returns_semantically_relevant_chunk() -> None:
    docs = [
        {"chunk_id": "quartz", "text": "石英 是 二氧化硅 矿物"},
        {"chunk_id": "calcite", "text": "方解石 是 碳酸盐 矿物"},
    ]

    results = DenseRetriever(docs, embedder=HashingEmbedder(dimensions=64)).search("石英 SiO2", top_k=1)

    assert results[0]["chunk_id"] == "quartz"
    assert "dense_score" in results[0]


def test_merge_ranked_results_combines_bm25_and_dense_without_duplicates() -> None:
    bm25_results = [
        {"chunk_id": "a", "score": 3.0, "text": "A"},
        {"chunk_id": "b", "score": 1.0, "text": "B"},
    ]
    dense_results = [
        {"chunk_id": "b", "dense_score": 0.9, "text": "B"},
        {"chunk_id": "c", "dense_score": 0.8, "text": "C"},
    ]

    merged = merge_ranked_results(bm25_results, dense_results, top_k=3)

    assert [row["chunk_id"] for row in merged] == ["b", "a", "c"]
    assert merged[0]["hybrid_score"] > merged[1]["hybrid_score"]


def test_hybrid_search_returns_ranked_chunks() -> None:
    docs = [
        {"chunk_id": "quartz", "text": "石英 二氧化硅 Raman 464"},
        {"chunk_id": "feldspar", "text": "长石 铝硅酸盐 框架振动"},
        {"chunk_id": "calcite", "text": "方解石 碳酸盐 1085"},
    ]

    results = hybrid_search("石英 Raman", docs, top_k=2, embedder=HashingEmbedder(dimensions=64))

    assert len(results) == 2
    assert results[0]["chunk_id"] == "quartz"


def test_lexical_reranker_promotes_more_overlapping_document() -> None:
    candidates = [
        {"chunk_id": "weak", "text": "石英 是 矿物"},
        {"chunk_id": "strong", "text": "石英 Raman 464 cm-1 二氧化硅"},
    ]

    reranked = LexicalReranker().rerank("石英 Raman 464", candidates, top_k=2)

    assert reranked[0]["chunk_id"] == "strong"
    assert reranked[0]["rerank_score"] > reranked[1]["rerank_score"]

