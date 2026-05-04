import os
from typing import Any

from minigeo.rag.http import Transport, parse_json_response, post_json


class EmbeddingServiceEmbedder:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 60.0,
        transport: Transport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.transport = transport or post_json
        self._cache: dict[str, list[float]] = {}

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors: list[list[float] | None] = [None] * len(texts)
        missing_positions: dict[str, list[int]] = {}
        for index, text in enumerate(texts):
            cached = self._cache.get(text)
            if cached is None:
                missing_positions.setdefault(text, []).append(index)
            else:
                vectors[index] = list(cached)

        if not missing_positions:
            return [list(vector) for vector in vectors if vector is not None]

        missing_texts = list(missing_positions)
        payload: dict[str, Any] = {
            "model": self.model,
            "input": missing_texts[0] if len(missing_texts) == 1 else missing_texts,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        response = parse_json_response(
            self.transport(f"{self.base_url}/embeddings", headers, payload, self.timeout)
        )
        try:
            embedded = [
                [float(value) for value in item["embedding"]]
                for item in response["data"]
            ]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Unexpected embedding response: {response}") from exc
        if len(embedded) != len(missing_texts):
            raise ValueError(f"Unexpected embedding response: {response}")
        for text, vector in zip(missing_texts, embedded):
            self._cache[text] = list(vector)
            for index in missing_positions[text]:
                vectors[index] = list(vector)
        if any(vector is None for vector in vectors):
            raise ValueError(f"Unexpected embedding response: {response}")
        return [list(vector) for vector in vectors if vector is not None]


def embedding_embedder_from_env(
    env: dict[str, str] | None = None,
    transport: Transport | None = None,
) -> EmbeddingServiceEmbedder:
    values = env if env is not None else os.environ
    base_url = values.get("MINIGEO_EMBEDDING_BASE_URL") or values.get("OPENAI_BASE_URL", "")
    base_url = base_url.strip()
    if not base_url:
        raise ValueError("MINIGEO_EMBEDDING_BASE_URL or OPENAI_BASE_URL is required.")
    return EmbeddingServiceEmbedder(
        base_url=base_url,
        api_key=values.get("MINIGEO_EMBEDDING_API_KEY") or values.get("OPENAI_API_KEY", "EMPTY"),
        model=values.get("MINIGEO_EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B"),
        timeout=float(values.get("MINIGEO_EMBEDDING_TIMEOUT", values.get("MINIGEO_LLM_TIMEOUT", "60"))),
        transport=transport,
    )
