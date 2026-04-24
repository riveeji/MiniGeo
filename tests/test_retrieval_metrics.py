from minigeo.eval.retrieval import citation_hit_rate, mrr, recall_at_k


def test_retrieval_metrics_use_gold_evidence_ids() -> None:
    gold = [{"id": "q1", "evidence": ["a"]}, {"id": "q2", "evidence": ["x"]}]
    retrieved = {"q1": ["b", "a"], "q2": ["y", "z"]}

    assert recall_at_k(gold, retrieved, k=2) == 0.5
    assert mrr(gold, retrieved) == 0.25
    assert citation_hit_rate(gold, {"q1": ["a"], "q2": ["z"]}) == 0.5

