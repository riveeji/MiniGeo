from pathlib import Path

from minigeo.finetune.lora_config import load_lora_config, validate_lora_config


def test_load_lora_config_reads_project_yaml_without_pyyaml() -> None:
    config = load_lora_config(Path("configs/qwen35_2b_lora.yaml"))

    assert config["model"]["base_model"] == "Qwen/Qwen3.5-2B"
    assert config["training"]["method"] == "qlora"
    assert config["data"]["train_path"] == "data/processed/sft_corpus.jsonl"


def test_validate_lora_config_accepts_current_project_paths() -> None:
    config = load_lora_config(Path("configs/qwen35_2b_lora.yaml"))

    assert validate_lora_config(config, root=Path(".")) == []


def test_validate_lora_config_reports_missing_data_and_wrong_method(tmp_path: Path) -> None:
    config = {
        "model": {"base_model": "Qwen/Qwen3.5-2B", "output_dir": "checkpoints/out"},
        "training": {"method": "full", "quantization": "4bit", "lora_rank": 16},
        "data": {"train_path": "missing_sft.jsonl", "eval_path": "missing_bench.jsonl"},
    }

    errors = validate_lora_config(config, root=tmp_path)

    assert "training.method 必须是 qlora" in errors
    assert "data.train_path 不存在：missing_sft.jsonl" in errors
    assert "data.eval_path 不存在：missing_bench.jsonl" in errors
