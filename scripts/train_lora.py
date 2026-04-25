import argparse
from pathlib import Path

from minigeo.finetune.lora_config import load_lora_config, validate_lora_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate MiniGeo QLoRA config and print Colab run hints.")
    parser.add_argument("--config", default="configs/qwen35_2b_lora.yaml")
    parser.add_argument("--check-only", action="store_true", help="Only validate local config and data paths.")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_lora_config(config_path)
    errors = validate_lora_config(config, root=Path("."))
    if errors:
        for error in errors:
            print(f"config_error={error}")
        raise SystemExit(2)

    print("QLoRA config check passed.")
    print(f"base_model={config['model']['base_model']}")
    print(f"train_path={config['data']['train_path']}")
    print(f"eval_path={config['data']['eval_path']}")
    print(f"output_dir={config['model']['output_dir']}")
    if args.check_only:
        return

    print("Colab preparation:")
    print("1. Install requirements-model.txt in a Python 3.10-3.12 GPU runtime.")
    print("2. Run python scripts/build_sft_corpus.py before training.")
    print("3. Start with a small smoke run before full QLoRA training.")


if __name__ == "__main__":
    main()
