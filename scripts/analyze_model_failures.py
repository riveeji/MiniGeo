import argparse
import json
from pathlib import Path

from minigeo.eval.model_failure_analysis import analyze_rag_failures, format_failure_analysis_markdown
from minigeo.jsonl import read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze saved model-service RAG citation failures.")
    parser.add_argument("--input", default="results/model_service_qwen35_4b_150_rag.jsonl")
    parser.add_argument("--output", default="results/model_failure_analysis_150.md")
    parser.add_argument("--max-examples", type=int, default=12)
    args = parser.parse_args()

    records = read_jsonl(Path(args.input))
    report = analyze_rag_failures(records, max_examples=args.max_examples)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(format_failure_analysis_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False))
    print(f"wrote={output}")


if __name__ == "__main__":
    main()
