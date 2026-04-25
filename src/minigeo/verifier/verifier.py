from typing import Any

from minigeo.verifier.claim_extractor import LocalClaimExtractor
from minigeo.verifier.evidence_matcher import EvidenceMatcher
from minigeo.verifier.support_classifier import HeuristicSupportClassifier


class MiniGeoVerifier:
    def __init__(
        self,
        claim_extractor: Any | None = None,
        evidence_matcher: EvidenceMatcher | None = None,
        support_classifier: Any | None = None,
        top_k: int = 3,
    ):
        self.claim_extractor = claim_extractor or LocalClaimExtractor()
        self.evidence_matcher = evidence_matcher or EvidenceMatcher()
        self.support_classifier = support_classifier or HeuristicSupportClassifier()
        self.top_k = top_k

    def verify(self, answer: str, evidence_chunks: list[dict[str, Any]]) -> dict[str, Any]:
        claims = self.claim_extractor.extract(answer)
        verified = []
        for claim in claims:
            matches = self.evidence_matcher.match(claim, evidence_chunks, top_k=self.top_k)
            result = self.support_classifier.classify(claim, matches)
            verified.append(result.to_dict())
        return {
            "verdict": _verdict(verified),
            "claims": verified,
        }


def _verdict(claims: list[dict[str, Any]]) -> str:
    if not claims:
        return "insufficient_evidence"
    statuses = [claim["status"] for claim in claims]
    if all(status == "supported" for status in statuses):
        return "supported"
    if any(status == "contradicted" for status in statuses):
        return "contradicted"
    if any(status == "supported" for status in statuses):
        return "partially_supported"
    return "insufficient_evidence"

