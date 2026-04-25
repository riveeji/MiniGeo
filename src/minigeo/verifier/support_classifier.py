import json
from typing import Any, Protocol

from minigeo.verifier.types import ClaimVerification


class TextGenerator(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class HeuristicSupportClassifier:
    def __init__(self, min_score: float = 0.2):
        self.min_score = min_score

    def classify(self, claim: str, matched_evidence: list[dict[str, Any]]) -> ClaimVerification:
        usable = [row for row in matched_evidence if row.get("match_score", 0.0) >= self.min_score]
        if not usable:
            return ClaimVerification(claim=claim, status="insufficient", evidence=[], confidence=0.0)
        best_score = max(row.get("match_score", 0.0) for row in usable)
        return ClaimVerification(
            claim=claim,
            status="supported",
            evidence=[row["chunk_id"] for row in usable],
            confidence=max(0.0, min(1.0, float(best_score))),
        )


class ModelSupportClassifier:
    VALID_STATUSES = {"supported", "contradicted", "insufficient"}

    def __init__(self, client: TextGenerator, fallback: HeuristicSupportClassifier | None = None):
        self.client = client
        self.fallback = fallback or HeuristicSupportClassifier()

    def classify(self, claim: str, matched_evidence: list[dict[str, Any]]) -> ClaimVerification:
        evidence_text = "\n".join(
            f"[{row['chunk_id']}] {row.get('text', '')}" for row in matched_evidence
        )
        prompt = (
            "判断 claim 是否被证据支持。"
            "只返回 JSON 对象："
            '{"status":"supported|contradicted|insufficient","evidence":["chunk_id"],"confidence":0.0}\n\n'
            f"Claim: {claim}\n\nEvidence:\n{evidence_text}"
        )
        raw = self.client.generate(prompt)
        try:
            data = json.loads(raw)
            status = str(data["status"])
            if status not in self.VALID_STATUSES:
                raise ValueError(status)
            allowed_ids = {row["chunk_id"] for row in matched_evidence}
            evidence = [item for item in data.get("evidence", []) if item in allowed_ids]
            confidence = max(0.0, min(1.0, float(data.get("confidence", 0.0))))
            return ClaimVerification(claim=claim, status=status, evidence=evidence, confidence=confidence)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return self.fallback.classify(claim, matched_evidence)

