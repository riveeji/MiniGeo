from minigeo.eval.retrieval_failure_analysis import (
    analyze_retrieval_failures,
    format_retrieval_failure_report,
)


def test_analyze_retrieval_failures_classifies_label_narrow_cases() -> None:
    benchmark = [
        {
            "id": "q1",
            "question": "石英 Raman 峰",
            "evidence": ["doc_quartz#chunk_001"],
        }
    ]
    corpus = [
        {"chunk_id": "doc_quartz#chunk_001", "doc_id": "doc_quartz", "text": "石英 Raman 464 cm-1"},
        {"chunk_id": "doc_quartz#chunk_002", "doc_id": "doc_quartz", "text": "石英 二氧化硅 光谱"},
    ]
    outputs = {"bm25": {"q1": ["doc_quartz#chunk_002"]}}

    report = analyze_retrieval_failures(benchmark, corpus, outputs, top_k=1)

    assert report["summary"]["bm25"]["misses"] == 1
    assert report["summary"]["bm25"]["categories"]["evidence_label_narrow"] == 1
    assert report["cases"][0]["retrieved_ids"] == ["doc_quartz#chunk_002"]


def test_analyze_retrieval_failures_classifies_reranker_demotions() -> None:
    benchmark = [{"id": "q1", "question": "calcite", "evidence": ["gold"]}]
    corpus = [
        {"chunk_id": "gold", "doc_id": "doc_calcite", "text": "calcite carbonate"},
        {"chunk_id": "near", "doc_id": "doc_other", "text": "other carbonate"},
    ]
    outputs = {
        "hybrid": {"q1": ["gold", "near"]},
        "hybrid_rerank": {"q1": ["near"]},
    }

    report = analyze_retrieval_failures(benchmark, corpus, outputs, top_k=1)

    assert report["summary"]["hybrid_rerank"]["categories"]["reranker_demoted_gold"] == 1
    assert report["cases"][0]["category"] == "reranker_demoted_gold"


def test_format_retrieval_failure_report_contains_summary_and_cases() -> None:
    report = {
        "summary": {
            "bm25": {
                "items": 2,
                "misses": 1,
                "miss_rate": 0.5,
                "categories": {"retrieval_gold_missing": 1},
            }
        },
        "cases": [
            {
                "system": "bm25",
                "id": "q1",
                "question": "石英是什么？",
                "expected_evidence": ["gold"],
                "retrieved_ids": ["miss"],
                "category": "retrieval_gold_missing",
                "suspected_cause": "检索排序未把 gold evidence 放入 top-k。",
                "next_action": "补充同义词或语料。",
            }
        ],
    }

    markdown = format_retrieval_failure_report(report)

    assert "# MiniGeo 检索失败分析" in markdown
    assert "| bm25 | 2 | 1 | 0.500 |" in markdown
    assert "retrieval_gold_missing" in markdown
