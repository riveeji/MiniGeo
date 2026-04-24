from minigeo.verifier.simple import verify_answer
from minigeo.verifier.types import ClaimVerification


def test_claim_verification_to_dict() -> None:
    item = ClaimVerification(
        claim="石英硬度高",
        status="supported",
        evidence=["doc_1#chunk_1"],
        confidence=0.9,
    )

    assert item.to_dict()["evidence"] == ["doc_1#chunk_1"]


def test_simple_verifier_marks_insufficient_when_no_evidence() -> None:
    report = verify_answer("石英硬度高。", [])

    assert report["verdict"] == "insufficient_evidence"
    assert report["claims"][0]["status"] == "insufficient"

