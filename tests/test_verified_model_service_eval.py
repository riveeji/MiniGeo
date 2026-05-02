from minigeo.eval.verified_model_service import format_verified_model_report, verify_saved_model_records


class FakeVerifier:
    def verify(self, answer, evidence):
        if "unsupported" in answer:
            return {"verdict": "insufficient_evidence", "claims": [{"status": "insufficient"}]}
        return {"verdict": "supported", "claims": [{"status": "supported"}]}


def test_verify_saved_model_records_adds_verification_to_each_result() -> None:
    records = [
        {
            "id": "q1",
            "question": "问题1",
            "gold_evidence": ["doc_a"],
            "result": {
                "answer": "supported answer",
                "citations": ["doc_a"],
                "abstained": False,
                "confidence": 0.8,
                "evidence": [{"chunk_id": "doc_a", "text": "supported answer"}],
            },
        },
        {
            "id": "q2",
            "question": "问题2",
            "gold_evidence": ["doc_b"],
            "result": {
                "answer": "unsupported answer",
                "citations": ["doc_b"],
                "abstained": False,
                "confidence": 0.8,
                "evidence": [{"chunk_id": "doc_b", "text": "other"}],
            },
        },
    ]

    verified = verify_saved_model_records(records, verifier=FakeVerifier())

    assert verified[0]["result"]["verifier_action"] == "accepted"
    assert verified[1]["result"]["verifier_action"] == "abstained"
    assert verified[1]["result"]["unverified_answer"] == "unsupported answer"


def test_format_verified_model_report_includes_model_and_verifier_metrics() -> None:
    report = format_verified_model_report(
        model_summary={"items": 2, "citation_hit_rate": 0.5, "abstention_accuracy": 1.0, "request_errors": 0},
        verifier_summary={"unsupported_claim_rate": 0.25, "verdicts": {"supported": 1, "insufficient_evidence": 1}},
        output_path="results/out.jsonl",
    )

    assert "MiniGeo RAG + Verifier 离线评测" in report
    assert "verifier_mode" in report
    assert "citation_hit_rate" in report
    assert "unsupported_claim_rate" in report
    assert "results/out.jsonl" in report
