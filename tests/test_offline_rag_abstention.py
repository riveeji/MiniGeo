from minigeo.rag.pipeline import offline_rag_answer


def test_offline_rag_abstains_for_unknown_sample_identifier() -> None:
    corpus = [{"chunk_id": "doc_quartz#chunk_001", "text": "石英的主要成分是二氧化硅。"}]

    result = offline_rag_answer("当前资料库能否确定样本 PX-101 的矿物类别？", corpus)

    assert result["abstained"] is True
    assert result["citations"] == []


def test_offline_rag_answers_when_relevant_evidence_exists() -> None:
    corpus = [{"chunk_id": "doc_quartz#chunk_001", "text": "石英的主要成分是二氧化硅。"}]

    result = offline_rag_answer("石英的主要成分是什么？", corpus)

    assert result["abstained"] is False
    assert result["citations"] == ["doc_quartz#chunk_001"]
