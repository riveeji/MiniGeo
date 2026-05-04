from scripts.evaluate_retrieval_ablation import _service_usage


def test_service_usage_supports_staged_embedding_and_reranker_services() -> None:
    assert _service_usage(use_services=False, use_embedding_service=True, use_reranker_service=False) == (True, False)
    assert _service_usage(use_services=False, use_embedding_service=False, use_reranker_service=True) == (False, True)
    assert _service_usage(use_services=True, use_embedding_service=False, use_reranker_service=False) == (True, True)
