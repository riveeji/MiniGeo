from pathlib import Path


def test_adapter_dir_validation_requires_config_and_weights(tmp_path: Path) -> None:
    from minigeo.finetune.adapter_eval import validate_adapter_dir

    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    (adapter_dir / "adapter_config.json").write_text("{}", encoding="utf-8")

    assert validate_adapter_dir(adapter_dir) == ["missing adapter_model.safetensors"]

    (adapter_dir / "adapter_model.safetensors").write_bytes(b"fake")

    assert validate_adapter_dir(adapter_dir) == []


def test_build_sft_prompt_requests_json_only() -> None:
    from minigeo.finetune.adapter_eval import build_sft_prompt

    prompt = build_sft_prompt("石英的主要成分是什么？")

    assert "Output only one JSON object" in prompt
    assert "answer, citations, abstained, confidence" in prompt
    assert "石英的主要成分是什么？" in prompt


def test_format_sft_adapter_report_marks_passed_artifact() -> None:
    from minigeo.finetune.adapter_eval import format_sft_adapter_report

    markdown = format_sft_adapter_report(
        adapter_dir=Path("checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter"),
        summary={
            "items": 2,
            "non_empty_answer_rate": 1.0,
            "citation_hit_rate": 0.5,
            "abstention_accuracy": 1.0,
            "request_errors": 0,
            "latency_ms": 12.5,
        },
        records_path=Path("results/sft_adapter_smoke.jsonl"),
        dry_run=False,
    )

    assert "# MiniGeo SFT Adapter Smoke Evaluation" in markdown
    assert "MiniGeo-Qwen3.5-2B-SFT-128step" in markdown
    assert "citation_hit_rate=0.500" in markdown
    assert "results/sft_adapter_smoke.jsonl" in markdown


def test_parse_adapter_answer_merges_multiple_json_objects_and_short_citation_ids() -> None:
    from minigeo.finetune.adapter_eval import parse_adapter_answer

    raw = (
        '{"answer": "石英的主要化学成分是二氧化硅 SiO2。"}\n'
        '{"citations": [{"id": "quartz#chunk_001"}]}\n'
        '{"abstained": false, "confidence": 0.95}\n'
        "</think>\n\n"
        '{"answer": "石英的主要化学成分是二氧化硅 SiO2。"}'
    )

    parsed = parse_adapter_answer(raw, allowed_citations={"doc_quartz#chunk_001"})

    assert parsed["answer"] == "石英的主要化学成分是二氧化硅 SiO2。"
    assert parsed["citations"] == ["doc_quartz#chunk_001"]
    assert parsed["abstained"] is False
    assert parsed["confidence"] == 0.95


def test_parse_adapter_answer_extracts_allowed_source_from_non_json_fragment() -> None:
    from minigeo.finetune.adapter_eval import parse_adapter_answer

    raw = (
        '{"answer": "赤铁矿是铁氧化物矿物。"}\n'
        '{"citations": []}\n'
        '{"abstained": false, "confidence": 0.5}\n'
        '{"source": [doc_hematite#chunk_001]}'
    )

    parsed = parse_adapter_answer(raw, allowed_citations={"doc_hematite#chunk_001"})

    assert parsed["answer"] == "赤铁矿是铁氧化物矿物。"
    assert parsed["citations"] == ["doc_hematite#chunk_001"]
    assert parsed["abstained"] is False
    assert parsed["confidence"] == 0.5


def test_reparse_adapter_records_preserves_raw_and_updates_result() -> None:
    from minigeo.finetune.adapter_eval import reparse_adapter_records

    records = [
        {
            "id": "minigeo_001",
            "gold_evidence": ["doc_quartz#chunk_001"],
            "result": {
                "raw_model_output": (
                    '{"answer": "石英的主要化学成分是二氧化硅 SiO2。"}\n'
                    '{"citations": [{"id": "quartz#chunk_001"}]}\n'
                    '{"abstained": false, "confidence": 0.95}'
                )
            },
        }
    ]

    reparsed = reparse_adapter_records(records)

    assert reparsed[0]["result"]["answer"] == "石英的主要化学成分是二氧化硅 SiO2。"
    assert reparsed[0]["result"]["citations"] == ["doc_quartz#chunk_001"]
    assert reparsed[0]["result"]["raw_model_output"] == records[0]["result"]["raw_model_output"]
