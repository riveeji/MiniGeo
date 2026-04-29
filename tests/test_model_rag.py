from minigeo.rag.model_rag import assemble_json_rag_prompt, generate_model_rag_answer, parse_model_answer


class FakeClient:
    def __init__(self, content: str):
        self.content = content
        self.prompts = []
        self.kwargs = []

    def generate(self, prompt: str, **kwargs) -> str:
        self.prompts.append(prompt)
        self.kwargs.append(kwargs)
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


def test_parse_model_answer_normalizes_bracketed_json_citations() -> None:
    raw = '{"answer":"石英主要成分是二氧化硅。","citations":["[doc_quartz#chunk_001]"],"abstained":false,"confidence":0.9}'

    parsed = parse_model_answer(raw, allowed_citations={"doc_quartz#chunk_001"})

    assert parsed["citations"] == ["doc_quartz#chunk_001"]


def test_parse_model_answer_rejects_thinking_only_fallback() -> None:
    raw = "Thinking Process:\n先分析证据。\n没有最终 JSON。"

    parsed = parse_model_answer(raw, allowed_citations={"doc_quartz#chunk_001"})

    assert parsed["answer"] == ""
    assert parsed["abstained"] is True
    assert parsed["format_error"] is True


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
    assert client.kwargs[0]["temperature"] == 0.0
    assert "JSON API" in client.kwargs[0]["system"]


def test_assemble_json_rag_prompt_requires_direct_citation_support() -> None:
    prompt = assemble_json_rag_prompt(
        "识别方解石时为什么需要证据来源？",
        [
            {"chunk_id": "doc_calcite#chunk_001", "text": "方解石是典型碳酸盐矿物。"},
            {"chunk_id": "doc_system#chunk_001", "text": "RAG 回答返回 chunk id 可以追踪证据。"},
        ],
    )

    assert "直接支撑" in prompt
    assert "不要引用泛化的系统说明" in prompt


def test_generate_model_rag_answer_repairs_generic_system_citation_to_domain_evidence() -> None:
    corpus = [
        {
            "chunk_id": "doc_calcite#chunk_001",
            "doc_id": "doc_calcite",
            "text": "方解石是典型碳酸盐矿物，不属于硅酸盐矿物。",
            "topic": "concept",
            "mineral": "calcite",
            "source": "seed",
        },
        {
            "chunk_id": "doc_system#chunk_001",
            "doc_id": "doc_system",
            "text": "RAG 回答返回 chunk id 可以让答案证据来源可追踪，便于检查引用是否支持结论。",
            "topic": "system",
            "mineral": "",
            "source": "seed",
        },
    ]
    client = FakeClient(
        '{"answer":"识别方解石时需要证据来源，因为方解石是典型碳酸盐矿物，引用可让结论可追踪。",'
        '"citations":["doc_system#chunk_001"],"abstained":false,"confidence":0.8}'
    )

    result = generate_model_rag_answer("识别方解石时为什么需要证据来源？", corpus, client, top_k=2)

    assert result["citations"] == ["doc_calcite#chunk_001"]


def test_generate_model_rag_answer_drops_generic_system_citation_when_domain_citation_exists() -> None:
    corpus = [
        {
            "chunk_id": "doc_quartz#chunk_001",
            "doc_id": "doc_quartz",
            "text": "石英是常见的硅酸盐矿物，主要化学成分是二氧化硅 SiO2。",
            "topic": "concept",
            "mineral": "quartz",
            "source": "seed",
        },
        {
            "chunk_id": "doc_system#chunk_001",
            "doc_id": "doc_system",
            "text": "RAG 回答返回 chunk id 可以让答案证据来源可追踪，便于检查引用是否支持结论。",
            "topic": "system",
            "mineral": "",
            "source": "seed",
        },
    ]
    client = FakeClient(
        '{"answer":"石英主要化学成分是二氧化硅。",'
        '"citations":["doc_quartz#chunk_001","doc_system#chunk_001"],"abstained":false,"confidence":0.9}'
    )

    result = generate_model_rag_answer("石英的主要成分是什么？", corpus, client, top_k=2)

    assert result["citations"] == ["doc_quartz#chunk_001"]
