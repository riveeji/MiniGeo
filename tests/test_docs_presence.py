from pathlib import Path


def test_agent_design_doc_covers_tools_demo_and_metrics() -> None:
    text = Path("docs/agent-design.md").read_text(encoding="utf-8")

    assert "search_docs" in text
    assert "execute_sql" in text
    assert "verify_answer" in text
    assert "Qinhuangdao" in text
    assert "sql_exec_accuracy" in text
    assert "scripts/evaluate_agent_cases.py" in text


def test_architecture_doc_lists_local_evaluation_entrypoints() -> None:
    text = Path("docs/architecture.md").read_text(encoding="utf-8")

    assert "scripts/audit_project.py" in text
    assert "scripts/analyze_retrieval_failures.py" in text


def test_showcase_doc_summarizes_results_and_remaining_a100_tasks() -> None:
    text = Path("docs/project-showcase.md").read_text(encoding="utf-8")

    assert "Qwen3-Embedding-0.6B hybrid retrieval" in text
    assert "检索失败分析" in text
    assert "Qwen3-Reranker-0.6B" in text
    assert "QLoRA smoke run" in text
    assert "MiniGeo-Agent 多案例评测" in text
    assert "sft-adapter-eval-runbook" in text
    assert "简历表述" in text
