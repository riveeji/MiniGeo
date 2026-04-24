from dataclasses import dataclass


@dataclass
class ClaimVerification:
    claim: str
    status: str
    evidence: list[str]
    confidence: float

    def to_dict(self) -> dict:
        return {
            "claim": self.claim,
            "status": self.status,
            "evidence": self.evidence,
            "confidence": self.confidence,
        }

