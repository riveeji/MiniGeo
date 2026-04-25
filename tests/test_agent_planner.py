from minigeo.agent.planner import plan_agent_tools


def test_agent_planner_routes_hybrid_analysis_question() -> None:
    plan = plan_agent_tools(
        "Analyze which mineral categories are most frequently misclassified in samples collected from Qinhuangdao, "
        "and explain possible causes using spectral evidence."
    )

    assert plan["requires_sql"] is True
    assert plan["requires_docs"] is True
    assert plan["requires_verification"] is True
    assert plan["mode"] == "hybrid"


def test_agent_planner_routes_document_question() -> None:
    plan = plan_agent_tools("石英的主要化学成分是什么？")

    assert plan["requires_sql"] is False
    assert plan["requires_docs"] is True
    assert plan["mode"] == "docs"


def test_agent_planner_routes_sql_question() -> None:
    plan = plan_agent_tools("每个地区有多少错误预测？")

    assert plan["requires_sql"] is True
    assert plan["requires_docs"] is False
    assert plan["mode"] == "sql"
