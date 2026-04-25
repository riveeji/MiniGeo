from pathlib import Path


def test_agent_design_doc_covers_tools_demo_and_metrics() -> None:
    text = Path("docs/agent-design.md").read_text(encoding="utf-8")

    assert "search_docs" in text
    assert "execute_sql" in text
    assert "verify_answer" in text
    assert "Qinhuangdao" in text
    assert "sql_exec_accuracy" in text
