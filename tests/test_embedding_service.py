from minigeo.rag.embedding_service import EmbeddingServiceEmbedder, embedding_embedder_from_env


def test_embedding_service_posts_openai_compatible_payload() -> None:
    captured = {}

    def fake_transport(url, headers, payload, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = payload
        captured["timeout"] = timeout
        return {"data": [{"embedding": [0.1, 0.2, 0.3]}]}

    embedder = EmbeddingServiceEmbedder(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY",
        model="Qwen/Qwen3-Embedding-0.6B",
        transport=fake_transport,
    )

    vector = embedder.embed("石英 二氧化硅")

    assert vector == [0.1, 0.2, 0.3]
    assert captured["url"] == "http://localhost:8000/v1/embeddings"
    assert captured["headers"]["Authorization"] == "Bearer EMPTY"
    assert captured["payload"]["model"] == "Qwen/Qwen3-Embedding-0.6B"
    assert captured["payload"]["input"] == "石英 二氧化硅"


def test_embedding_service_supports_batch_embedding() -> None:
    def fake_transport(url, headers, payload, timeout):
        return {"data": [{"embedding": [1.0, 0.0]}, {"embedding": [0.0, 1.0]}]}

    embedder = EmbeddingServiceEmbedder(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY",
        model="Qwen/Qwen3-Embedding-0.6B",
        transport=fake_transport,
    )

    assert embedder.embed_batch(["石英", "方解石"]) == [[1.0, 0.0], [0.0, 1.0]]


def test_embedding_service_caches_repeated_texts() -> None:
    calls = {"count": 0}

    def fake_transport(url, headers, payload, timeout):
        calls["count"] += 1
        return {"data": [{"embedding": [0.3, 0.7]}]}

    embedder = EmbeddingServiceEmbedder(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY",
        model="Qwen/Qwen3-Embedding-0.6B",
        transport=fake_transport,
    )

    assert embedder.embed("quartz") == [0.3, 0.7]
    assert embedder.embed("quartz") == [0.3, 0.7]
    assert calls["count"] == 1


def test_embedding_embedder_from_env_uses_embedding_specific_defaults() -> None:
    embedder = embedding_embedder_from_env(
        {
            "OPENAI_BASE_URL": "http://localhost:8000/v1",
            "OPENAI_API_KEY": "EMPTY",
            "MINIGEO_EMBEDDING_MODEL": "Qwen/Qwen3-Embedding-0.6B",
        },
        transport=lambda url, headers, payload, timeout: {"data": [{"embedding": [0.5]}]},
    )

    assert embedder.model == "Qwen/Qwen3-Embedding-0.6B"
    assert embedder.embed("test") == [0.5]
