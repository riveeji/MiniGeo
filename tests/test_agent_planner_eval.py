from minigeo.eval.agent_planner import planner_sql_accuracy, summarize_planner_routes


def test_planner_sql_accuracy_compares_requires_sql_flag() -> None:
    rows = [
        {"id": "q1", "question": "每个地区有多少错误预测？", "requires_sql": True},
        {"id": "q2", "question": "石英的主要成分是什么？", "requires_sql": False},
    ]

    assert planner_sql_accuracy(rows) == 1.0


def test_summarize_planner_routes_counts_modes_and_latency() -> None:
    summary = summarize_planner_routes(
        [
            {"id": "q1", "question": "每个地区有多少错误预测？", "requires_sql": True},
            {"id": "q2", "question": "石英的主要成分是什么？", "requires_sql": False},
        ],
        latency_ms=0.2,
    )

    assert summary["items"] == 2
    assert summary["sql_routing_accuracy"] == 1.0
    assert summary["modes"]["sql"] == 1
    assert summary["modes"]["docs"] == 1
    assert summary["latency_ms"] == 0.2
