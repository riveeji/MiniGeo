from minigeo.rag.bm25 import BM25Retriever
from minigeo.rag.tokenizer import tokenize


def test_tokenize_handles_chinese_without_spaces() -> None:
    tokens = tokenize("石英具有较高硬度")

    assert "石英" in tokens or "石" in tokens
    assert len(tokens) >= 2


def test_bm25_returns_relevant_chinese_chunk() -> None:
    docs = [
        {"chunk_id": "quartz", "text": "石英 具有 较高 硬度 二氧化硅"},
        {"chunk_id": "calcite", "text": "方解石 碳酸盐 遇 稀盐酸 起泡"},
    ]

    results = BM25Retriever(docs).search("石英 硬度", top_k=1)

    assert results[0]["chunk_id"] == "quartz"
    assert results[0]["score"] > 0


def test_bm25_expands_failure_case_analysis_query() -> None:
    docs = [
        {"chunk_id": "system_failure", "text": "失败案例分析应区分数据缺失、检索失败、生成错误、验证误判和 SQL 错误。"},
        {"chunk_id": "pyrite", "text": "黄铁矿的金属光泽不能单独证明其为金或氧化物。"},
    ]

    results = BM25Retriever(docs).search("为什么需要 failure case analysis？", top_k=1)

    assert results[0]["chunk_id"] == "system_failure"


def test_bm25_expands_mineral_evidence_query() -> None:
    docs = [
        {"chunk_id": "feldspar_concept", "text": "长石是一类铝硅酸盐框架矿物，常见于火成岩和变质岩。"},
        {"chunk_id": "muscovite_property", "text": "片状解理可以辅助识别白云母，但可信回答仍需要证据来源。"},
    ]

    results = BM25Retriever(docs).search("识别长石时为什么需要证据来源？", top_k=1)

    assert results[0]["chunk_id"] == "feldspar_concept"


def test_bm25_expands_feldspar_spectroscopy_query() -> None:
    docs = [
        {"chunk_id": "feldspar_spectra", "text": "长石与石英同属硅酸盐体系，部分框架振动特征可能接近，弱峰和噪声会增加混淆风险。"},
        {"chunk_id": "anorthite_property", "text": "钙长石属于长石族，回答时应避免把它误归为碳酸盐矿物。"},
    ]

    results = BM25Retriever(docs).search("长石相关光谱或性质证据在回答中有什么作用？", top_k=1)

    assert results[0]["chunk_id"] == "feldspar_spectra"
