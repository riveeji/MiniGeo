from minigeo.rag.reranker_service import RerankerService, reranker_from_env


def test_reranker_service_posts_query_and_documents() -> None:
    captured = {}

    def fake_transport(url, headers, payload, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = payload
        return {
            "results": [
                {"index": 1, "relevance_score": 0.95},
                {"index": 0, "relevance_score": 0.20},
            ]
        }

    reranker = RerankerService(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY",
        model="Qwen/Qwen3-Reranker-0.6B",
        transport=fake_transport,
    )
    candidates = [
        {"chunk_id": "weak", "text": "石英 是 矿物"},
        {"chunk_id": "strong", "text": "石英 Raman 464 cm-1"},
    ]

    results = reranker.rerank("石英 Raman 464", candidates, top_k=2)

    assert results[0]["chunk_id"] == "strong"
    assert results[0]["rerank_score"] == 0.95
    assert captured["url"] == "http://localhost:8000/v1/rerank"
    assert captured["headers"]["Authorization"] == "Bearer EMPTY"
    assert captured["payload"]["model"] == "Qwen/Qwen3-Reranker-0.6B"
    assert captured["payload"]["query"] == "石英 Raman 464"
    assert captured["payload"]["documents"] == ["石英 是 矿物", "石英 Raman 464 cm-1"]


def test_reranker_from_env_uses_reranker_specific_defaults() -> None:
    reranker = reranker_from_env(
        {
            "OPENAI_BASE_URL": "http://localhost:8000/v1",
            "OPENAI_API_KEY": "EMPTY",
            "MINIGEO_RERANKER_MODEL": "Qwen/Qwen3-Reranker-0.6B",
        },
        transport=lambda url, headers, payload, timeout: {"results": [{"index": 0, "relevance_score": 1.0}]},
    )

    results = reranker.rerank("query", [{"chunk_id": "a", "text": "query"}], top_k=1)

    assert reranker.model == "Qwen/Qwen3-Reranker-0.6B"
    assert results[0]["chunk_id"] == "a"

