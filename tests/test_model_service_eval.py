from minigeo.eval.model_service import summarize_model_rag_outputs
from scripts.evaluate_model_service import select_benchmark_rows


def test_summarize_model_rag_outputs_counts_valid_json_and_citations() -> None:
    rows = [{"id": "q1", "evidence": ["doc_a"]}, {"id": "q2", "evidence": ["doc_b"]}]
    outputs = {
        "q1": {"answer": "ok", "citations": ["doc_a"], "abstained": False, "raw_model_output": "{}"},
        "q2": {"answer": "", "citations": [], "abstained": True, "raw_model_output": ""},
    }

    summary = summarize_model_rag_outputs(rows, outputs, latency_ms=12.0)

    assert summary["items"] == 2
    assert summary["non_empty_answer_rate"] == 0.5
    assert summary["citation_hit_rate"] == 0.5
    assert summary["citation_items"] == 2
    assert summary["empty_raw_outputs"] == 1
    assert summary["latency_ms"] == 12.0


def test_summarize_model_rag_outputs_uses_evidence_denominator_for_citation_hit() -> None:
    rows = [
        {"id": "q1", "evidence": ["doc_a"]},
        {"id": "q2", "evidence": []},
    ]
    outputs = {
        "q1": {"answer": "ok", "citations": ["doc_a"], "abstained": False, "raw_model_output": "{}"},
        "q2": {"answer": "ok", "citations": [], "abstained": False, "raw_model_output": "{}"},
    }

    summary = summarize_model_rag_outputs(rows, outputs)

    assert summary["citation_items"] == 1
    assert summary["citation_hit_rate"] == 1.0


def test_select_benchmark_rows_supports_phase2_selection_modes() -> None:
    rows = [
        {"id": "q1", "answerable": True, "evidence": ["doc_a"]},
        {"id": "q2", "answerable": False, "evidence": []},
        {"id": "q3", "answerable": True, "evidence": []},
    ]

    assert [row["id"] for row in select_benchmark_rows(rows, "evidence", 10)] == ["q1"]
    assert [row["id"] for row in select_benchmark_rows(rows, "all", 2)] == ["q1", "q2"]
    assert [row["id"] for row in select_benchmark_rows(rows, "unanswerable", 10)] == ["q2"]
