import json
from pathlib import Path

from minigeo.finetune.qlora_smoke import build_smoke_plan, format_sft_example, load_sft_rows


def test_load_sft_rows_limits_training_examples(tmp_path: Path) -> None:
    path = tmp_path / "sft.jsonl"
    path.write_text(
        "\n".join(
            json.dumps(
                {
                    "id": f"sft_{index}",
                    "instruction": "根据证据回答。",
                    "input": f"[doc#chunk_{index}] evidence",
                    "output": "answer",
                },
                ensure_ascii=False,
            )
            for index in range(5)
        ),
        encoding="utf-8",
    )

    rows = load_sft_rows(path, limit=2)

    assert [row["id"] for row in rows] == ["sft_0", "sft_1"]


def test_format_sft_example_contains_instruction_input_and_output() -> None:
    text = format_sft_example(
        {
            "instruction": "根据给定证据写摘要。",
            "input": "[doc_quartz#chunk_001] 石英含 SiO2。",
            "output": "石英主要成分是 SiO2。[doc_quartz#chunk_001]",
        }
    )

    assert "MiniGeo" in text
    assert "根据给定证据写摘要。" in text
    assert "[doc_quartz#chunk_001] 石英含 SiO2。" in text
    assert "石英主要成分是 SiO2。[doc_quartz#chunk_001]" in text


def test_build_smoke_plan_uses_config_and_cli_overrides() -> None:
    config = {
        "model": {"base_model": "Qwen/Qwen3.5-2B", "output_dir": "checkpoints/MiniGeo-Qwen3.5-2B-SFT"},
        "training": {"lora_rank": 16, "lora_alpha": 32, "lora_dropout": 0.05, "learning_rate": 0.0002},
        "data": {"train_path": "data/processed/sft_corpus.jsonl"},
    }

    plan = build_smoke_plan(config, sample_size=8, max_steps=3, output_dir="checkpoints/qlora-smoke")

    assert plan["base_model"] == "Qwen/Qwen3.5-2B"
    assert plan["train_path"] == "data/processed/sft_corpus.jsonl"
    assert plan["output_dir"] == "checkpoints/qlora-smoke"
    assert plan["sample_size"] == 8
    assert plan["max_steps"] == 3
    assert plan["lora_rank"] == 16
