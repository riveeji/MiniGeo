from minigeo.eval.model_failure_analysis import analyze_rag_failures, format_failure_analysis_markdown


def test_analyze_rag_failures_classifies_retrieval_and_model_causes() -> None:
    records = [
        {
            "id": "q1",
            "question": "q1",
            "gold_evidence": ["gold"],
            "result": {
                "answer": "ok",
                "citations": ["other"],
                "abstained": False,
                "evidence": [{"chunk_id": "other", "doc_id": "doc_other"}],
            },
        },
        {
            "id": "q2",
            "question": "q2",
            "gold_evidence": ["doc_a#chunk_001"],
            "result": {
                "answer": "证据不足",
                "citations": [],
                "abstained": True,
                "evidence": [{"chunk_id": "doc_a#chunk_001", "doc_id": "doc_a"}],
            },
        },
        {
            "id": "q3",
            "question": "q3",
            "gold_evidence": ["doc_a#chunk_001"],
            "result": {
                "answer": "ok",
                "citations": ["doc_a#chunk_002"],
                "abstained": False,
                "evidence": [{"chunk_id": "doc_a#chunk_001", "doc_id": "doc_a"}],
            },
        },
    ]

    report = analyze_rag_failures(records)

    assert report["total_records"] == 3
    assert report["citation_misses"] == 3
    assert report["categories"]["retrieval_gold_missing"] == 1
    assert report["categories"]["model_abstained_with_gold"] == 1
    assert report["categories"]["model_cited_neighbor"] == 1


def test_format_failure_analysis_markdown_includes_examples() -> None:
    markdown = format_failure_analysis_markdown(
        {
            "total_records": 1,
            "citation_misses": 1,
            "categories": {"retrieval_gold_missing": 1},
            "examples": [
                {
                    "id": "q1",
                    "category": "retrieval_gold_missing",
                    "question": "问题",
                    "gold": ["doc_a#chunk_001"],
                    "citations": [],
                    "retrieved": ["doc_b#chunk_001"],
                    "answer": "证据不足",
                }
            ],
        }
    )

    assert "MiniGeo 模型失败分析" in markdown
    assert "retrieval_gold_missing" in markdown
    assert "q1" in markdown
