import json

from minigeo.finetune.sft import build_sft_examples, find_reference_answer_leaks


def test_build_sft_examples_does_not_copy_benchmark_reference_answers() -> None:
    benchmark = [
        {
            "id": "q1",
            "question": "资料库是否包含未知样本？",
            "answer": "当前资料库没有未知样本证据，不能确认。",
            "answerable": False,
            "requires_sql": False,
            "expected_sql_intent": None,
        },
        {
            "id": "q2",
            "question": "查询错误预测。",
            "answer": "使用 SQL 查询错误预测。",
            "answerable": True,
            "requires_sql": True,
            "expected_sql_intent": "filter incorrect predictions",
            "evidence": ["doc_q#chunk_1"],
        },
        {
            "id": "q3",
            "question": "石英的证据是什么？",
            "answer": "石英是二氧化硅矿物。",
            "answerable": True,
            "requires_sql": False,
            "expected_sql_intent": None,
            "evidence": ["doc_q#chunk_1"],
        },
    ]
    corpus = [
        {"chunk_id": "doc_q#chunk_1", "text": "石英是二氧化硅矿物。", "topic": "concept"},
    ]

    examples = build_sft_examples(benchmark, corpus)
    leaks = find_reference_answer_leaks(examples, benchmark)

    assert examples
    assert leaks == []
    assert any(example["task_type"] == "refusal" for example in examples)
    assert any(example["task_type"] == "sql_format" for example in examples)
    assert any(example["task_type"] == "evidence_summary" for example in examples)
    assert any(example["task_type"] == "evidence_qa" for example in examples)
    assert any(example["task_type"] == "verification_rewrite" for example in examples)
    assert all({"id", "instruction", "input", "output", "task_type"} <= set(example) for example in examples)
    assert all("doc_q#chunk_1" in example["output"] for example in examples if example["task_type"] == "evidence_qa")
    assert all(example["output"] != row["answer"] for example in examples for row in benchmark)


def test_build_sft_examples_outputs_single_json_contract_without_thinking_tags() -> None:
    benchmark = [
        {
            "id": "q_evidence",
            "question": "石英的证据是什么？",
            "answer": "石英是二氧化硅矿物。",
            "answerable": True,
            "requires_sql": False,
            "expected_sql_intent": None,
            "evidence": ["doc_q#chunk_1"],
        },
        {
            "id": "q_refusal",
            "question": "不存在的矿物有什么拉曼峰？",
            "answer": "不能确认。",
            "answerable": False,
            "requires_sql": False,
            "expected_sql_intent": None,
            "evidence": [],
        },
        {
            "id": "q_sql",
            "question": "查询错误预测。",
            "answer": "使用 SQL 查询错误预测。",
            "answerable": True,
            "requires_sql": True,
            "expected_sql_intent": "filter incorrect predictions",
            "evidence": ["doc_q#chunk_1"],
        },
    ]
    corpus = [{"chunk_id": "doc_q#chunk_1", "text": "石英是二氧化硅矿物。", "topic": "concept"}]

    examples = build_sft_examples(benchmark, corpus)

    assert examples
    for example in examples:
        output = example["output"]
        assert "<think" not in output.lower()
        assert "</think>" not in output.lower()
        assert output.count("{") == 1
        assert output.count("}") == 1
        parsed = json.loads(output)
        assert set(parsed) == {"answer", "citations", "abstained", "confidence"}
        assert isinstance(parsed["answer"], str)
        assert isinstance(parsed["citations"], list)
        assert isinstance(parsed["abstained"], bool)
        assert isinstance(parsed["confidence"], float | int)
        assert "Output exactly one JSON object" in example["instruction"]
        assert "If the answer says evidence is insufficient, abstained must be true" in example["instruction"]


def test_build_sft_examples_keeps_task_type_distribution_balanced() -> None:
    benchmark = []
    corpus = []
    for index in range(1, 6):
        chunk_id = f"doc_{index}#chunk_001"
        corpus.append({"chunk_id": chunk_id, "text": f"证据 {index}。", "topic": "concept"})
        benchmark.append(
            {
                "id": f"q_evidence_{index}",
                "question": f"证据题 {index}？",
                "answer": f"参考答案 {index}",
                "answerable": True,
                "requires_sql": False,
                "expected_sql_intent": None,
                "evidence": [chunk_id],
            }
        )
        benchmark.append(
            {
                "id": f"q_sql_{index}",
                "question": f"SQL 题 {index}？",
                "answer": f"SQL 参考答案 {index}",
                "answerable": True,
                "requires_sql": True,
                "expected_sql_intent": f"intent_{index}",
                "evidence": [chunk_id],
            }
        )
        benchmark.append(
            {
                "id": f"q_refusal_{index}",
                "question": f"不可回答题 {index}？",
                "answer": f"拒答参考答案 {index}",
                "answerable": False,
                "requires_sql": False,
                "expected_sql_intent": None,
                "evidence": [],
            }
        )

    examples = build_sft_examples(benchmark, corpus)
    counts = {}
    for example in examples:
        counts[example["task_type"]] = counts.get(example["task_type"], 0) + 1

    assert set(counts) == {"evidence_summary", "refusal", "sql_format", "evidence_qa", "verification_rewrite"}
    assert max(counts.values()) / len(examples) < 0.6


def test_find_reference_answer_leaks_detects_exact_output_copy() -> None:
    examples = [{"id": "sft_bad", "output": "石英是二氧化硅矿物。"}]
    benchmark = [{"id": "q1", "answer": "石英是二氧化硅矿物。"}]

    assert find_reference_answer_leaks(examples, benchmark) == ["sft_bad"]
