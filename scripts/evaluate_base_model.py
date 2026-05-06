import argparse
import json
from pathlib import Path

from minigeo.finetune.adapter_eval import format_base_model_report, run_base_smoke


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a base Qwen model on the MiniGeo SFT smoke subset.")
    parser.add_argument("--base-model", default="Qwen/Qwen3.5-2B")
    parser.add_argument("--benchmark", default="data/benchmark/minigeo_bench.jsonl")
    parser.add_argument("--corpus", default="data/processed/rag_corpus.jsonl")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--output", default="results/base_qwen35_2b_smoke10.jsonl")
    parser.add_argument("--report", default="results/base_qwen35_2b_smoke10.md")
    parser.add_argument("--dry-run", action="store_true", help="Write selected prompts without loading model weights.")
    args = parser.parse_args()

    summary = run_base_smoke(
        base_model=args.base_model,
        benchmark_path=Path(args.benchmark),
        output_path=Path(args.output),
        limit=args.limit,
        max_new_tokens=args.max_new_tokens,
        corpus_path=Path(args.corpus),
        dry_run=args.dry_run,
    )
    report = format_base_model_report(
        base_model=args.base_model,
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
