from typing import Any

from minigeo.rag.tokenizer import tokenize


class EvidenceMatcher:
    def match(self, claim: str, evidence_chunks: list[dict[str, Any]], top_k: int = 3) -> list[dict[str, Any]]:
        claim_tokens = set(tokenize(claim))
        if not claim_tokens:
            return []
        scored: list[dict[str, Any]] = []
        for chunk in evidence_chunks:
            chunk_tokens = set(tokenize(str(chunk.get("text", ""))))
            if not chunk_tokens:
                score = 0.0
            else:
                overlap = len(claim_tokens & chunk_tokens)
                score = overlap / max(1, len(claim_tokens))
            item = dict(chunk)
            item["match_score"] = score
            scored.append(item)
        return sorted(scored, key=lambda item: item["match_score"], reverse=True)[:top_k]

