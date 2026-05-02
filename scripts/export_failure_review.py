import argparse
import csv
import json
from pathlib import Path

from minigeo.eval.failure_review import REVIEW_FIELDS, build_failure_review_rows, format_failure_review_markdown
from minigeo.jsonl import read_jsonl


DEFAULT_CATEGORIES = {"model_cited_neighbor", "model_cited_other"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export citation-miss rows for manual benchmark/evidence review.")
    parser.add_argument("--input", default="results/model_service_qwen35_4b_150_rag.jsonl")
    parser.add_argument("--csv-output", default="results/model_failure_review_150.csv")
    parser.add_argument("--markdown-output", default="results/model_failure_review_150.md")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=sorted(DEFAULT_CATEGORIES),
        help="Failure categories to export, or 'all'.",
    )
    args = parser.parse_args()

    records = read_jsonl(Path(args.input))
    categories = None if "all" in args.categories else set(args.categories)
    rows = build_failure_review_rows(records, categories=categories)

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    markdown_output = Path(args.markdown_output)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.write_text(format_failure_review_markdown(rows), encoding="utf-8", newline="\n")

    summary = {
        "items": len(rows),
        "categories": sorted(categories) if categories is not None else "all",
        "csv_output": str(csv_output),
        "markdown_output": str(markdown_output),
    }
    print(json.dumps(summary, ensure_ascii=False))
    print(f"wrote={csv_output}")
    print(f"wrote={markdown_output}")


if __name__ == "__main__":
    main()
