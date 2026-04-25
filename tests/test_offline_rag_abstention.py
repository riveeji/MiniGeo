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


def test_offline_rag_abstains_for_sample_coverage_question_without_exact_evidence() -> None:
    corpus = [{"chunk_id": "doc_quartz#chunk_002", "text": "石英常见强拉曼峰接近 464 cm-1。"}]

    result = offline_rag_answer("资料库是否包含金刚石样本的拉曼峰？", corpus)

    assert result["abstained"] is True


def test_offline_rag_abstains_for_complete_infrared_peak_requests() -> None:
    corpus = [{"chunk_id": "doc_olivine#chunk_002", "text": "橄榄石的部分光谱特征可用于辅助识别。"}]

    result = offline_rag_answer("橄榄石在本语料库中的主要红外峰是什么？", corpus)

    assert result["abstained"] is True
