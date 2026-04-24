import os
from typing import Any

from minigeo.rag.http import Transport, parse_json_response, post_json


class RerankerService:
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

    def rerank(self, query: str, candidates: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
        payload = {
            "model": self.model,
            "query": query,
            "documents": [str(row.get("text", "")) for row in candidates],
            "top_n": top_k,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        response = parse_json_response(
            self.transport(f"{self.base_url}/rerank", headers, payload, self.timeout)
        )
        try:
            results = response["results"]
        except KeyError as exc:
            raise ValueError(f"Unexpected reranker response: {response}") from exc

        reranked: list[dict[str, Any]] = []
        for result in results:
            index = int(result["index"])
            if index < 0 or index >= len(candidates):
                continue
            row = dict(candidates[index])
            row["rerank_score"] = float(result["relevance_score"])
            reranked.append(row)
        return sorted(reranked, key=lambda item: item["rerank_score"], reverse=True)[:top_k]


def reranker_from_env(
    env: dict[str, str] | None = None,
    transport: Transport | None = None,
) -> RerankerService:
    values = env if env is not None else os.environ
    base_url = values.get("MINIGEO_RERANKER_BASE_URL") or values.get("OPENAI_BASE_URL", "")
    base_url = base_url.strip()
    if not base_url:
        raise ValueError("MINIGEO_RERANKER_BASE_URL or OPENAI_BASE_URL is required.")
    return RerankerService(
        base_url=base_url,
        api_key=values.get("MINIGEO_RERANKER_API_KEY") or values.get("OPENAI_API_KEY", "EMPTY"),
        model=values.get("MINIGEO_RERANKER_MODEL", "Qwen/Qwen3-Reranker-0.6B"),
        timeout=float(values.get("MINIGEO_RERANKER_TIMEOUT", values.get("MINIGEO_LLM_TIMEOUT", "60"))),
        transport=transport,
    )

