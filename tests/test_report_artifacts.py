from minigeo.eval.report_artifacts import format_failure_cases, format_main_results


def test_format_main_results_includes_local_baselines() -> None:
    markdown = format_main_results(
        retrieval={
            "bm25": {"citation_hit_rate": 0.924, "latency_ms": 1.2},
            "hybrid": {"citation_hit_rate": 0.876, "latency_ms": 2.5},
        },
        verifier={"unsupported_claim_rate": 0.557},
        sql={"sql_exec_accuracy": 1.0},
        agent_demo_passed=True,
    )

    assert "# MiniGeo 主结果" in markdown
    assert "BM25 RAG baseline" in markdown
    assert "0.924" in markdown
    assert "1.200 ms/q" in markdown
    assert "MiniGeo-Agent demo" in markdown


def test_format_failure_cases_limits_cases_and_keeps_schema() -> None:
    markdown = format_failure_cases(
        [
            {
                "case_id": "retrieval_001",
                "question": "q",
                "system": "bm25",
                "observed_output": "miss",
                "expected_behavior": "hit",
                "failure_type": "retrieval_miss",
                "suspected_cause": "missing synonym",
                "next_action": "add data",
            }
        ]
    )

    assert "# MiniGeo 失败案例" in markdown
    assert "case_id: retrieval_001" in markdown
    assert "failure_type: retrieval_miss" in markdown
