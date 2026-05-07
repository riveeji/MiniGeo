from minigeo.eval.report_artifacts import abstention_failure_cases, format_failure_cases, format_main_results
from scripts.write_report_artifacts import (
    _saved_base_model_rows,
    _saved_json64_evidence_sft_adapter_rows,
    _saved_json64_sft_adapter_rows,
    _saved_retrieval_service_rows,
    _saved_sft_adapter_rows,
)


def test_format_main_results_includes_local_baselines() -> None:
    markdown = format_main_results(
        retrieval={
            "bm25": {"citation_hit_rate": 0.924, "latency_ms": 1.2},
            "hybrid": {"citation_hit_rate": 0.876, "latency_ms": 2.5},
        },
        verifier={"unsupported_claim_rate": 0.557, "latency_ms": 0.8},
        sql={"sql_exec_accuracy": 1.0, "latency_ms": 0.4},
        abstention={"abstention_accuracy": 0.75},
        planner={"sql_routing_accuracy": 0.9, "latency_ms": 0.01},
        agent_demo_passed=True,
        agent_latency_ms=5.0,
        agent_cases={"pass_rate": 1.0, "latency_ms": 7.5},
        extra_rows=[("Qwen3.5-4B + BM25 RAG", "", 0.833, "", 0.9, "-", "见 model_service_eval")],
    )

    assert "# MiniGeo 主结果" in markdown
    assert "BM25 RAG baseline" in markdown
    assert "0.924" in markdown
    assert "1.200 ms/q" in markdown
    assert "0.800 ms/q" in markdown
    assert "0.400 ms/q" in markdown
    assert "0.750" in markdown
    assert "Planner baseline" in markdown
    assert "0.900" in markdown
    assert "5.000 ms/q" in markdown
    assert "MiniGeo-Agent demo" in markdown
    assert "MiniGeo-Agent multi-case" in markdown
    assert "7.500 ms/q" in markdown
    assert "Qwen3.5-4B + BM25 RAG" in markdown


def test_format_main_results_omits_completed_model_verifier_from_pending_list() -> None:
    markdown = format_main_results(
        retrieval={},
        verifier={},
        sql={},
        abstention={},
        planner={},
        agent_demo_passed=True,
        extra_rows=[
            (
                "Qwen3.5-4B + BM25 RAG + Model Verifier",
                "",
                0.665,
                0.022,
                0.740,
                "-",
                "见 model_service_model_verified_eval",
            )
        ],
    )

    pending_section = markdown.split("## 待补充模型结果", 1)[1]

    assert "Qwen3.5-4B + BM25 RAG + Model Verifier" in markdown
    assert "模型辅助 Verifier 复判结果" not in pending_section


def test_format_main_results_marks_embedding_service_as_completed() -> None:
    markdown = format_main_results(
        retrieval={},
        verifier={},
        sql={},
        abstention={},
        planner={},
        agent_demo_passed=True,
        extra_rows=[("Qwen3-Embedding-0.6B dense retrieval", "", 0.957, "", "", "-", "见 retrieval_service_eval")],
    )

    pending_section = markdown.split("## 待补充模型结果", 1)[1]

    assert "真实 Qwen3-Embedding / Qwen3-Reranker 服务消融结果" not in pending_section
    assert "真实 Qwen3-Reranker 服务消融结果" in pending_section


def test_saved_retrieval_service_rows_prefers_explicit_report_rows(tmp_path) -> None:
    path = tmp_path / "retrieval_service_eval.json"
    path.write_text(
        """
{
  "main_result_rows": [
    {
      "system": "Qwen3-Reranker-0.6B hybrid rerank",
      "citation_hit_rate": 0.93,
      "latency": "见 retrieval_service_eval"
    }
  ],
  "metrics": {
    "dense": {"citation_hit_rate": 0.1}
  }
}
""",
        encoding="utf-8",
    )

    rows = _saved_retrieval_service_rows(path)

    assert rows == [("Qwen3-Reranker-0.6B hybrid rerank", "", 0.93, "", "", "-", "见 retrieval_service_eval")]


def test_saved_sft_adapter_rows_reads_smoke_jsonl_and_report(tmp_path) -> None:
    output_path = tmp_path / "sft_adapter_128step_smoke10.jsonl"
    report_path = tmp_path / "sft_adapter_128step_smoke10.md"
    output_path.write_text(
        "\n".join(
            [
                '{"id":"q1","gold_evidence":["doc_a#chunk_001"],"result":{"answer":"a","citations":["doc_a#chunk_001"],"abstained":false,"raw_model_output":"raw"}}',
                '{"id":"q2","gold_evidence":[],"result":{"answer":"b","citations":[],"abstained":true,"raw_model_output":"raw"}}',
            ]
        ),
        encoding="utf-8",
    )
    report_path.write_text("- latency_ms=12.500\n", encoding="utf-8")

    rows = _saved_sft_adapter_rows(output_path, report_path)

    assert rows == [("MiniGeo-2B-SFT 128step smoke", "", 1.0, "", 1.0, "-", "12.500 ms/q")]


def test_saved_base_model_rows_reads_smoke_jsonl_and_report(tmp_path) -> None:
    output_path = tmp_path / "base_qwen35_2b_smoke10.jsonl"
    report_path = tmp_path / "base_qwen35_2b_smoke10.md"
    output_path.write_text(
        "\n".join(
            [
                '{"id":"q1","gold_evidence":["doc_a#chunk_001"],"result":{"answer":"a","citations":["doc_a#chunk_001"],"abstained":false,"raw_model_output":"raw"}}',
                '{"id":"q2","gold_evidence":[],"result":{"answer":"b","citations":[],"abstained":true,"raw_model_output":"raw"}}',
            ]
        ),
        encoding="utf-8",
    )
    report_path.write_text("- latency_ms=20.000\n", encoding="utf-8")

    rows = _saved_base_model_rows(output_path, report_path)

    assert rows == [("Qwen3.5-2B base smoke", "", 1.0, "", 1.0, "-", "20.000 ms/q")]


def test_saved_json64_sft_adapter_rows_reads_smoke_jsonl_and_report(tmp_path) -> None:
    output_path = tmp_path / "sft_adapter_json64_smoke10_reparsed.jsonl"
    report_path = tmp_path / "sft_adapter_json64_smoke10.md"
    output_path.write_text(
        "\n".join(
            [
                '{"id":"q1","gold_evidence":["doc_a#chunk_001"],"result":{"answer":"a","citations":["doc_a#chunk_001"],"abstained":false,"raw_model_output":"raw"}}',
                '{"id":"q2","gold_evidence":[],"result":{"answer":"b","citations":[],"abstained":false,"raw_model_output":"raw"}}',
            ]
        ),
        encoding="utf-8",
    )
    report_path.write_text("- latency_ms=30.000\n", encoding="utf-8")

    rows = _saved_json64_sft_adapter_rows(output_path, report_path)

    assert rows == [("MiniGeo-2B-SFT json64 smoke", "", 1.0, "", 0.5, "-", "30.000 ms/q")]


def test_saved_json64_evidence_sft_adapter_rows_reads_smoke_jsonl_and_report(tmp_path) -> None:
    output_path = tmp_path / "sft_adapter_json64_evidence_smoke10_reparsed.jsonl"
    report_path = tmp_path / "sft_adapter_json64_evidence_smoke10.md"
    output_path.write_text(
        "\n".join(
            [
                '{"id":"q1","gold_evidence":["doc_a#chunk_001"],"result":{"answer":"a","citations":["doc_a#chunk_001"],"abstained":false,"raw_model_output":"raw"}}',
                '{"id":"q2","gold_evidence":[],"result":{"answer":"b","citations":[],"abstained":true,"raw_model_output":"raw"}}',
            ]
        ),
        encoding="utf-8",
    )
    report_path.write_text("- latency_ms=40.000\n", encoding="utf-8")

    rows = _saved_json64_evidence_sft_adapter_rows(output_path, report_path)

    assert rows == [("MiniGeo-2B-SFT json64 evidence smoke", "", 1.0, "", 1.0, "-", "40.000 ms/q")]


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
