import argparse
import json
from pathlib import Path

from minigeo.finetune.adapter_eval import (
    format_sft_adapter_report,
    run_adapter_smoke,
    validate_adapter_dir,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a MiniGeo PEFT/QLoRA adapter on a small benchmark subset.")
    parser.add_argument("--adapter-dir", required=True)
    parser.add_argument("--base-model", default="Qwen/Qwen3.5-2B")
    parser.add_argument("--benchmark", default="data/benchmark/minigeo_bench.jsonl")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--output", default="results/sft_adapter_smoke.jsonl")
    parser.add_argument("--report", default="results/sft_adapter_smoke.md")
    parser.add_argument("--dry-run", action="store_true", help="Write selected prompts without loading model weights.")
    parser.add_argument("--check-only", action="store_true", help="Validate adapter files and exit.")
    args = parser.parse_args()

    adapter_dir = Path(args.adapter_dir)
    errors = validate_adapter_dir(adapter_dir)
    if args.check_only:
        print(json.dumps({"adapter_dir": str(adapter_dir), "errors": errors}, ensure_ascii=False, indent=2))
        if errors:
            raise SystemExit(2)
        return

    summary = run_adapter_smoke(
        adapter_dir=adapter_dir,
        base_model=args.base_model,
        benchmark_path=Path(args.benchmark),
        output_path=Path(args.output),
        limit=args.limit,
        max_new_tokens=args.max_new_tokens,
        dry_run=args.dry_run,
    )
    report = format_sft_adapter_report(
        adapter_dir=adapter_dir,
        summary=summary,
        records_path=Path(args.output),
        dry_run=args.dry_run,
    )
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(report, encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote={args.output}")
    print(f"wrote={args.report}")


if __name__ == "__main__":
    main()
