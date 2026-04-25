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


def test_agent_planner_does_not_route_conceptual_sample_question_to_sql() -> None:
    plan = plan_agent_tools("为什么不能只根据一个弱峰判断未知样本一定是石英？")

    assert plan["requires_sql"] is False
    assert plan["mode"] == "docs"


def test_agent_planner_routes_explicit_query_questions_to_sql() -> None:
    plan = plan_agent_tools("查询每个矿物类别的关键光谱特征。")

    assert plan["requires_sql"] is True
    assert plan["mode"] == "sql"


def test_agent_planner_routes_list_and_statistical_questions_to_sql() -> None:
    assert plan_agent_tools("列出 Qinhuangdao 中所有预测错误的 sample_id。")["requires_sql"] is True
    assert plan_agent_tools("统计预测正确率。")["requires_sql"] is True


def test_agent_planner_keeps_conceptual_agent_question_out_of_sql() -> None:
    plan = plan_agent_tools("为什么 Agent 最终答案需要同时返回 SQL 和证据？")

    assert plan["requires_sql"] is False
    assert plan["mode"] == "docs"
