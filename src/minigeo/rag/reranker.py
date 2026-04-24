from typing import Any

from minigeo.rag.tokenizer import tokenize


class LexicalReranker:
    def rerank(self, query: str, candidates: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
        query_tokens = set(tokenize(query))
        scored: list[dict[str, Any]] = []
        for row in candidates:
            row_tokens = set(tokenize(str(row.get("text", ""))))
            overlap = len(query_tokens & row_tokens)
            denom = max(1, len(query_tokens))
            item = dict(row)
            item["rerank_score"] = overlap / denom
            scored.append(item)
        return sorted(scored, key=lambda item: item["rerank_score"], reverse=True)[:top_k]

