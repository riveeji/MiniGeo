from scripts.evaluate_retrieval_ablation import _build_service_report, _format_service_report, _service_usage


def test_service_usage_supports_staged_embedding_and_reranker_services() -> None:
    assert _service_usage(use_services=False, use_embedding_service=True, use_reranker_service=False) == (True, False)
    assert _service_usage(use_services=False, use_embedding_service=False, use_reranker_service=True) == (False, True)
    assert _service_usage(use_services=True, use_embedding_service=False, use_reranker_service=False) == (True, True)


def test_build_service_report_labels_embedding_only_run() -> None:
    report = _build_service_report(
        metrics={
            "dense": {"citation_hit_rate": 0.957, "latency_ms": 100.0},
            "hybrid": {"citation_hit_rate": 1.0, "latency_ms": 5.0},
            "hybrid_rerank": {"citation_hit_rate": 0.9, "latency_ms": 10.0},
        },
        mode="embedding_service",
        embedding_model="Qwen/Qwen3-Embedding-0.6B",
        reranker_model="Qwen/Qwen3-Reranker-0.6B",
        command="python scripts/evaluate_retrieval_ablation.py --use-embedding-service",
        run_date="2026-05-04",
    )

    assert report["main_result_rows"][0]["system"] == "Qwen3-Embedding-0.6B dense retrieval"
    assert report["main_result_rows"][1]["system"] == "Qwen3-Embedding-0.6B hybrid retrieval"
    assert report["main_result_rows"][2]["system"] == "Qwen3-Embedding-0.6B hybrid + lexical rerank"


def test_format_service_report_includes_reranker_only_status() -> None:
    report = _build_service_report(
        metrics={"hybrid_rerank": {"citation_hit_rate": 0.93, "latency_ms": 42.0}},
        mode="reranker_service",
        embedding_model="Qwen/Qwen3-Embedding-0.6B",
        reranker_model="Qwen/Qwen3-Reranker-0.6B",
        command="python scripts/evaluate_retrieval_ablation.py --use-reranker-service",
        run_date="2026-05-04",
    )

    markdown = _format_service_report(report)

    assert "Qwen3-Reranker-0.6B hybrid rerank" in markdown
    assert "0.930" in markdown
