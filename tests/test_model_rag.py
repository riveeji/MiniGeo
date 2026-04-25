from minigeo.rag.model_rag import generate_model_rag_answer, parse_model_answer


class FakeClient:
    def __init__(self, content: str):
        self.content = content
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.content


def test_parse_model_answer_extracts_json_contract() -> None:
    raw = '{"answer":"石英主要成分是二氧化硅。","citations":["doc_quartz#chunk_001"],"abstained":false,"confidence":0.82}'

    parsed = parse_model_answer(raw, allowed_citations={"doc_quartz#chunk_001"})

    assert parsed["answer"] == "石英主要成分是二氧化硅。"
    assert parsed["citations"] == ["doc_quartz#chunk_001"]
    assert parsed["abstained"] is False
    assert parsed["confidence"] == 0.82


def test_parse_model_answer_prefers_final_json_over_schema_example() -> None:
    raw = (
        'Thinking Process: schema {"answer":"string","citations":["chunk_id"],"abstained":false,"confidence":0.0}\n'
        "```json\n"
        '{"answer":"石英主要成分是二氧化硅。","citations":["doc_quartz#chunk_001"],"abstained":false,"confidence":0.9}\n'
        "```"
    )

    parsed = parse_model_answer(raw, allowed_citations={"doc_quartz#chunk_001"})

    assert parsed["answer"] == "石英主要成分是二氧化硅。"
    assert parsed["citations"] == ["doc_quartz#chunk_001"]


def test_generate_model_rag_answer_uses_retrieved_evidence_and_filters_citations() -> None:
    corpus = [
        {
            "chunk_id": "doc_quartz#chunk_001",
            "text": "石英是硅酸盐矿物，主要化学成分是二氧化硅 SiO2。",
            "source": "seed",
        },
        {
            "chunk_id": "doc_calcite#chunk_001",
            "text": "方解石是碳酸盐矿物。",
            "source": "seed",
        },
    ]
    client = FakeClient(
        '{"answer":"石英主要成分是二氧化硅。","citations":["doc_quartz#chunk_001","not_retrieved"],"abstained":false,"confidence":0.9}'
    )

    result = generate_model_rag_answer("石英的主要成分是什么？", corpus, client, top_k=1)

    assert result["citations"] == ["doc_quartz#chunk_001"]
    assert result["abstained"] is False
    assert "doc_quartz#chunk_001" in client.prompts[0]
    assert "JSON" in client.prompts[0]
