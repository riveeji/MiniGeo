from minigeo.eval.model_service import summarize_model_rag_outputs


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
    assert summary["empty_raw_outputs"] == 1
    assert summary["latency_ms"] == 12.0
