import re
from typing import Any

from minigeo.rag.tokenizer import tokenize
from minigeo.verifier.types import ClaimVerification

SUPPORTED = "supported"
INSUFFICIENT = "insufficient"


def extract_claims(answer: str) -> list[str]:
    claims = [part.strip() for part in re.split(r"[。.!?！？]\s*", answer) if part.strip()]
    return claims or [answer.strip()] if answer.strip() else []


def verify_answer(answer: str, evidence_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    claims = extract_claims(answer)
    if not evidence_chunks:
        return {
            "verdict": "insufficient_evidence",
            "claims": [
                ClaimVerification(claim=claim, status=INSUFFICIENT, evidence=[], confidence=0.0).to_dict()
                for claim in claims
            ],
        }

    evidence_tokens = {
        row["chunk_id"]: set(tokenize(str(row.get("text", ""))))
        for row in evidence_chunks
    }
    verified: list[dict] = []
    for claim in claims:
        claim_tokens = set(tokenize(claim))
        matches = [
            chunk_id
            for chunk_id, tokens in evidence_tokens.items()
            if claim_tokens and len(claim_tokens & tokens) / max(1, len(claim_tokens)) >= 0.2
        ]
        status = SUPPORTED if matches else INSUFFICIENT
        confidence = 0.8 if matches else 0.2
        verified.append(ClaimVerification(claim, status, matches, confidence).to_dict())

    if all(item["status"] == SUPPORTED for item in verified):
        verdict = "supported"
    elif any(item["status"] == SUPPORTED for item in verified):
        verdict = "partially_supported"
    else:
        verdict = "insufficient_evidence"
    return {"verdict": verdict, "claims": verified}

