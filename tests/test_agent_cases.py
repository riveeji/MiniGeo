from pathlib import Path

from minigeo.rag.corpus import load_corpus
from minigeo.sql.tools import init_demo_db


def test_agent_cases_evaluate_multiple_routes(tmp_path: Path) -> None:
    from minigeo.eval.agent_cases import DEFAULT_AGENT_CASES, evaluate_agent_cases

    db_path = tmp_path / "demo.sqlite"
    init_demo_db(db_path)
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))

    summary, reports = evaluate_agent_cases(DEFAULT_AGENT_CASES, db_path=db_path, corpus=corpus)

    assert summary["items"] == len(DEFAULT_AGENT_CASES)
    assert summary["pass_rate"] == 1.0
    assert summary["plan_mode_accuracy"] == 1.0
    assert summary["sql_success_rate"] == 1.0
    assert summary["verification_report_rate"] == 1.0
    assert {report["expected_mode"] for report in reports} == {"hybrid", "sql", "docs"}
    assert all(report["passed"] for report in reports)
    assert all(report["answer"] for report in reports)


def test_agent_cases_markdown_report_is_chinese(tmp_path: Path) -> None:
    from minigeo.eval.agent_cases import DEFAULT_AGENT_CASES, evaluate_agent_cases, format_agent_case_report

    db_path = tmp_path / "demo.sqlite"
    init_demo_db(db_path)
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))

    summary, reports = evaluate_agent_cases(DEFAULT_AGENT_CASES[:1], db_path=db_path, corpus=corpus)
    markdown = format_agent_case_report(summary, reports)

    assert "# MiniGeo-Agent 多案例本地评测" in markdown
    assert "| case_id | 期望模式 | 实际模式 | 通过 |" in markdown
    assert DEFAULT_AGENT_CASES[0]["case_id"] in markdown
