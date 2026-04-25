from typing import Any

from minigeo.verifier.claim_extractor import LocalClaimExtractor
from minigeo.verifier.verifier import MiniGeoVerifier


def extract_claims(answer: str) -> list[str]:
    return LocalClaimExtractor().extract(answer)


def verify_answer(answer: str, evidence_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    return MiniGeoVerifier().verify(answer, evidence_chunks)

