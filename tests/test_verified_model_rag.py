from minigeo.rag.verified_model_rag import verify_rag_answer


class FakeVerifier:
    def __init__(self, report: dict):
        self.report = report
        self.calls = []

    def verify(self, answer, evidence):
        self.calls.append((answer, evidence))
        return self.report


def test_verify_rag_answer_keeps_supported_answer() -> None:
    answer = {
        "answer": "石英主要成分是二氧化硅。",
        "citations": ["doc_quartz#chunk_001"],
        "abstained": False,
        "confidence": 0.8,
        "evidence": [{"chunk_id": "doc_quartz#chunk_001", "text": "石英主要成分是二氧化硅。"}],
    }
    verifier = FakeVerifier({"verdict": "supported", "claims": []})

    verified = verify_rag_answer(answer, verifier)

    assert verified["answer"] == "石英主要成分是二氧化硅。"
    assert verified["citations"] == ["doc_quartz#chunk_001"]
    assert verified["abstained"] is False
    assert verified["verifier_action"] == "accepted"
    assert verified["verification"]["verdict"] == "supported"
    assert verifier.calls


def test_verify_rag_answer_abstains_on_unsupported_verdict() -> None:
    answer = {
        "answer": "石英是碳酸盐矿物。",
        "citations": ["doc_quartz#chunk_001"],
        "abstained": False,
        "confidence": 0.7,
        "evidence": [{"chunk_id": "doc_quartz#chunk_001", "text": "石英是硅酸盐矿物。"}],
    }
    verifier = FakeVerifier(
        {
            "verdict": "insufficient_evidence",
            "claims": [{"claim": "石英是碳酸盐矿物", "status": "insufficient", "evidence": [], "confidence": 0.0}],
        }
    )

    verified = verify_rag_answer(answer, verifier)

    assert verified["abstained"] is True
    assert verified["citations"] == []
    assert verified["confidence"] == 0.0
    assert verified["unverified_answer"] == "石英是碳酸盐矿物。"
    assert "证据不足" in verified["answer"]
    assert verified["verifier_action"] == "abstained"


def test_verify_rag_answer_does_not_reverify_existing_abstention() -> None:
    answer = {
        "answer": "证据不足",
        "citations": [],
        "abstained": True,
        "confidence": 0.0,
        "evidence": [],
    }
    verifier = FakeVerifier({"verdict": "supported", "claims": []})

    verified = verify_rag_answer(answer, verifier)

    assert verified["abstained"] is True
    assert verified["verifier_action"] == "skipped_abstained"
    assert verifier.calls == []
