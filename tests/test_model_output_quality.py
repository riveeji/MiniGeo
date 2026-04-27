from minigeo.eval.model_output_quality import analyze_model_outputs, format_model_output_quality_markdown


def test_analyze_model_outputs_counts_quality_failures() -> None:
    records = [
        {
            "id": "q1",
            "gold_evidence": ["doc_a"],
            "result": {
                "answer": "Thinking Process:\n最终答案",
                "citations": ["doc_b"],
                "abstained": False,
                "raw_model_output": "Thinking Process:\n{}",
            },
        },
        {
            "id": "q2",
            "gold_evidence": ["doc_c"],
            "result": {
                "answer": "string",
                "citations": ["doc_c"],
                "abstained": True,
                "raw_model_output": "{}",
                "error": "timeout",
            },
        },
    ]
    benchmark = [
        {"id": "q1", "answerable": True},
        {"id": "q2", "answerable": True},
    ]

    summary = analyze_model_outputs(records, benchmark)

    assert summary["items"] == 2
    assert summary["citation_miss_count"] == 1
    assert summary["thinking_answer_count"] == 1
    assert summary["thinking_raw_count"] == 1
    assert summary["placeholder_answer_count"] == 1
    assert summary["request_errors"] == 1
    assert summary["abstention_error_count"] == 1


def test_format_model_output_quality_markdown_lists_modes() -> None:
    markdown = format_model_output_quality_markdown(
        {
            "rag": {
                "items": 2,
                "citation_miss_rate": 0.5,
                "thinking_answer_rate": 0.5,
                "placeholder_answer_rate": 0.0,
                "abstention_error_rate": 0.0,
                "request_errors": 0,
            }
        }
    )

    assert "MiniGeo 模型输出质量审计" in markdown
    assert "| rag | 2 | 0.500 | 0.500 | 0.000 | 0.000 | 0 |" in markdown
