from minigeo.eval.verifier_interceptions import build_interception_rows, format_interception_markdown


def test_build_interception_rows_exports_abstained_verifier_actions() -> None:
    records = [
        {
            "id": "q1",
            "question": "问题1",
            "gold_evidence": ["doc_a"],
            "result": {
                "answer": "证据不足",
                "unverified_answer": "原始答案",
                "citations": [],
                "abstained": True,
                "verifier_action": "abstained",
                "verification": {
                    "verdict": "insufficient_evidence",
                    "claims": [{"claim": "原始答案", "status": "insufficient", "evidence": []}],
                },
                "evidence": [{"chunk_id": "doc_a"}],
            },
        },
        {
            "id": "q2",
            "question": "问题2",
            "gold_evidence": ["doc_b"],
            "result": {
                "answer": "答案",
                "citations": ["doc_b"],
                "abstained": False,
                "verifier_action": "accepted",
                "verification": {"verdict": "supported", "claims": []},
                "evidence": [{"chunk_id": "doc_b"}],
            },
        },
    ]

    rows = build_interception_rows(records)

    assert len(rows) == 1
    assert rows[0]["id"] == "q1"
    assert rows[0]["verdict"] == "insufficient_evidence"
    assert rows[0]["unverified_answer"] == "原始答案"
    assert rows[0]["unsupported_claims"] == "原始答案"
    assert rows[0]["review_decision"] == ""


def test_format_interception_markdown_includes_review_labels() -> None:
    markdown = format_interception_markdown(
        [
            {
                "id": "q1",
                "question": "问题",
                "verdict": "insufficient_evidence",
                "unverified_answer": "原始答案",
                "final_answer": "证据不足",
                "unsupported_claims": "claim",
                "gold_evidence": "doc_a",
                "retrieved_evidence": "doc_a",
                "review_decision": "",
                "reviewer_note": "",
            }
        ]
    )

    assert "MiniGeo Verifier 拦截样例" in markdown
    assert "correct_reject" in markdown
    assert "false_reject" in markdown
    assert "q1" in markdown
