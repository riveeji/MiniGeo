from minigeo.eval.local_summary import format_markdown_summary


def test_format_markdown_summary_contains_core_metrics() -> None:
    markdown = format_markdown_summary(
        benchmark={"items": 150, "requires_sql": 30},
        retrieval={"bm25": {"recall@10": 0.9, "citation_hit_rate": 0.8}},
        verifier={"unsupported_claim_rate": 0.5},
        sql={"sql_exec_accuracy": 1.0},
    )

    assert "# MiniGeo 本地评测汇总" in markdown
    assert "150" in markdown
    assert "0.900" in markdown
    assert "1.000" in markdown
