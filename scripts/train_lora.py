from pathlib import Path

import yaml


def main() -> None:
    config_path = Path("configs/qwen35_2b_lora.yaml")
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    print("QLoRA training entrypoint prepared.")
    print(f"base_model={config['model']['base_model']}")
    print("Run this script in Colab Pro after installing GPU dependencies and mounting data.")


if __name__ == "__main__":
    main()

