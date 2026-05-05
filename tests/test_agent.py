from pathlib import Path

from minigeo.agent.simple_agent import MiniGeoAgent, write_report
from minigeo.rag.corpus import load_corpus
from minigeo.sql.tools import init_demo_db


def test_write_report_includes_sql_evidence_and_limitations() -> None:
    report = write_report(
        answer="Qinhuangdao errors are led by feldspar.",
        sql="select * from predictions",
        evidence=["doc_feldspar#chunk_001"],
        verification={"verdict": "supported", "claims": []},
        limitations=["Demo database is small."],
    )

    assert report["sql"] == "select * from predictions"
    assert report["evidence"] == ["doc_feldspar#chunk_001"]
    assert report["limitations"] == ["Demo database is small."]


def test_minigeo_agent_combines_sql_evidence_and_verification(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.sqlite"
    init_demo_db(db_path)
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))

    report = MiniGeoAgent(db_path=db_path, corpus=corpus).run(
        "Analyze which mineral categories are most frequently misclassified in samples collected from Qinhuangdao, "
        "and explain possible causes using spectral evidence."
    )

    assert "Qinhuangdao" in report["sql"]
    assert report["sql_result"]["error"] is None
    assert report["sql_result"]["execution_result"][0]["predicted_mineral"] == "feldspar"
    assert report["sql_result"]["execution_result"][0]["errors"] == 2
    assert report["evidence"]
    assert "agent_sql#result" in report["evidence"]
    assert "doc_feldspar#chunk_002" in report["evidence"]
    sql_claims = [
        claim for claim in report["verification"]["claims"]
        if "SQL" in claim["claim"] and "feldspar" in claim["claim"]
    ]
    assert sql_claims
    assert sql_claims[0]["status"] == "supported"
    assert "agent_sql#result" in sql_claims[0]["evidence"]
    assert report["verification"]["verdict"] in {
        "supported",
        "partially_supported",
        "unsupported",
        "contradicted",
        "insufficient_evidence",
    }


def test_minigeo_agent_docs_mode_answers_from_document_evidence(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.sqlite"
    init_demo_db(db_path)
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))

    report = MiniGeoAgent(db_path=db_path, corpus=corpus).run("石英的主要拉曼光谱证据是什么？")

    assert report["plan"]["mode"] == "docs"
    assert report["sql"] is None
    assert report["sql_result"]["execution_result"] == []
    assert "464 cm-1" in report["answer"]
    assert "SQL 查询返回" not in report["answer"]
    assert "doc_quartz#chunk_002" in report["evidence"]
