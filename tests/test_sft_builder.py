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


def test_find_reference_answer_leaks_detects_exact_output_copy() -> None:
    examples = [{"id": "sft_bad", "output": "石英是二氧化硅矿物。"}]
    benchmark = [{"id": "q1", "answer": "石英是二氧化硅矿物。"}]

    assert find_reference_answer_leaks(examples, benchmark) == ["sft_bad"]

