from minigeo.eval.report_artifacts import abstention_failure_cases, format_failure_cases, format_main_results


def test_format_main_results_includes_local_baselines() -> None:
    markdown = format_main_results(
        retrieval={
            "bm25": {"citation_hit_rate": 0.924, "latency_ms": 1.2},
            "hybrid": {"citation_hit_rate": 0.876, "latency_ms": 2.5},
        },
        verifier={"unsupported_claim_rate": 0.557, "latency_ms": 0.8},
        sql={"sql_exec_accuracy": 1.0, "latency_ms": 0.4},
        abstention={"abstention_accuracy": 0.75},
        agent_demo_passed=True,
        agent_latency_ms=5.0,
    )

    assert "# MiniGeo 主结果" in markdown
    assert "BM25 RAG baseline" in markdown
    assert "0.924" in markdown
    assert "1.200 ms/q" in markdown
    assert "0.800 ms/q" in markdown
    assert "0.400 ms/q" in markdown
    assert "0.750" in markdown
    assert "5.000 ms/q" in markdown
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


def test_abstention_failure_cases_capture_missed_abstain() -> None:
    cases = abstention_failure_cases(
        [{"id": "q1", "question": "资料库是否包含金刚石样本的拉曼峰？", "answerable": False}],
        {"q1": {"abstained": False, "citations": ["doc_quartz#chunk_002"]}},
    )

    assert cases[0]["case_id"] == "abstention_001"
    assert cases[0]["failure_type"] == "missed_abstain"
    assert "doc_quartz#chunk_002" in cases[0]["observed_output"]
