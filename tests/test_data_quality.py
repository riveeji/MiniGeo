from minigeo.eval.data_quality import audit_data_quality, format_data_quality_report


def test_audit_data_quality_reports_core_counts_and_no_leaks() -> None:
    benchmark = [
        {
            "id": "q1",
            "answer": "石英是二氧化硅。",
            "evidence": ["doc_quartz#chunk_001"],
            "answerable": True,
            "requires_sql": False,
        }
    ]
    corpus = [
        {
            "chunk_id": "doc_quartz#chunk_001",
            "doc_id": "doc_quartz",
            "text": "石英是二氧化硅。",
            "source": "curated",
            "url": "https://example.org",
            "page": None,
            "topic": "concept",
            "mineral": "quartz",
            "license": "public",
        }
    ]
    sft = [{"id": "sft_1", "output": "该证据可用于回答石英问题。"}]

    report = audit_data_quality(benchmark, corpus, sft)

    assert report["benchmark_items"] == 1
    assert report["corpus_chunks"] == 1
    assert report["sft_items"] == 1
    assert report["missing_evidence_refs"] == []
    assert report["reference_answer_leaks"] == []
    assert report["metadata_missing"] == []


def test_format_data_quality_report_contains_actionable_sections() -> None:
    markdown = format_data_quality_report(
        {
            "benchmark_items": 1,
            "corpus_chunks": 1,
            "sft_items": 1,
            "missing_evidence_refs": ["q1:missing"],
            "reference_answer_leaks": ["sft_1"],
            "metadata_missing": ["chunk_1:url"],
        }
    )

    assert "# MiniGeo 数据质量审计" in markdown
    assert "q1:missing" in markdown
    assert "sft_1" in markdown
    assert "chunk_1:url" in markdown
