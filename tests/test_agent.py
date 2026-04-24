from minigeo.agent.simple_agent import write_report


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

