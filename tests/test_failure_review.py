from minigeo.eval.failure_review import build_failure_review_rows, format_failure_review_markdown


def test_build_failure_review_rows_filters_target_categories() -> None:
    records = [
        {
            "id": "q1",
            "question": "问题1",
            "gold_evidence": ["doc_a#chunk_001"],
            "result": {
                "answer": "答案1",
                "citations": ["doc_a#chunk_002"],
                "abstained": False,
                "evidence": [{"chunk_id": "doc_a#chunk_001"}, {"chunk_id": "doc_a#chunk_002"}],
            },
        },
        {
            "id": "q2",
            "question": "问题2",
            "gold_evidence": ["doc_b#chunk_001"],
            "result": {
                "answer": "答案2",
                "citations": [],
                "abstained": True,
                "evidence": [{"chunk_id": "doc_b#chunk_001"}],
            },
        },
    ]

    rows = build_failure_review_rows(records, categories={"model_cited_neighbor"})

    assert len(rows) == 1
    assert rows[0]["id"] == "q1"
    assert rows[0]["category"] == "model_cited_neighbor"
    assert rows[0]["gold_evidence"] == "doc_a#chunk_001"
    assert rows[0]["citations"] == "doc_a#chunk_002"
    assert rows[0]["review_decision"] == ""
    assert rows[0]["suggested_evidence"] == ""


def test_format_failure_review_markdown_includes_review_protocol() -> None:
    markdown = format_failure_review_markdown(
        [
            {
                "id": "q1",
                "category": "model_cited_other",
                "question": "问题",
                "gold_evidence": "doc_a#chunk_001",
                "citations": "doc_b#chunk_001",
                "retrieved_evidence": "doc_a#chunk_001, doc_b#chunk_001",
                "answer": "答案",
                "review_decision": "",
                "suggested_evidence": "",
                "reviewer_note": "",
            }
        ]
    )

    assert "MiniGeo 失败样例人工抽检表" in markdown
    assert "label_expand" in markdown
    assert "model_error" in markdown
    assert "q1" in markdown
