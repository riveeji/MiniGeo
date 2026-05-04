import argparse
import json
from pathlib import Path

from minigeo.finetune.lora_config import load_lora_config, validate_lora_config
from minigeo.finetune.qlora_smoke import build_smoke_plan, run_qlora_smoke


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small QLoRA smoke training job on Colab/A100.")
    parser.add_argument("--config", default="configs/qwen35_2b_lora.yaml")
    parser.add_argument("--sample-size", type=int, default=32)
    parser.add_argument("--max-steps", type=int, default=5)
    parser.add_argument("--output-dir", default="checkpoints/qlora-smoke")
    parser.add_argument("--dry-run", action="store_true", help="Print the smoke plan without loading model weights.")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_lora_config(config_path)
    errors = validate_lora_config(config, root=Path("."))
    if errors:
        for error in errors:
            print(f"config_error={error}")
        raise SystemExit(2)
    plan = build_smoke_plan(
        config,
        sample_size=args.sample_size,
        max_steps=args.max_steps,
        output_dir=args.output_dir,
    )
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if args.dry_run:
        return
    run_qlora_smoke(plan)


if __name__ == "__main__":
    main()
