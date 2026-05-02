import argparse
import csv
import json
from pathlib import Path

from minigeo.eval.verifier_interceptions import (
    INTERCEPTION_FIELDS,
    build_interception_rows,
    format_interception_markdown,
)
from minigeo.jsonl import read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Export RAG answers intercepted by Verifier for manual review.")
    parser.add_argument("--input", default="results/model_service_qwen35_4b_150_rag_verified.jsonl")
    parser.add_argument("--csv-output", default="results/verifier_interceptions_150.csv")
    parser.add_argument("--markdown-output", default="results/verifier_interceptions_150.md")
    args = parser.parse_args()

    records = read_jsonl(Path(args.input))
    rows = build_interception_rows(records)

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INTERCEPTION_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    markdown_output = Path(args.markdown_output)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.write_text(format_interception_markdown(rows), encoding="utf-8", newline="\n")

    print(json.dumps({"items": len(rows), "csv_output": str(csv_output), "markdown_output": str(markdown_output)}, ensure_ascii=False))
    print(f"wrote={csv_output}")
    print(f"wrote={markdown_output}")


if __name__ == "__main__":
    main()
