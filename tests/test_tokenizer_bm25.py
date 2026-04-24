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

