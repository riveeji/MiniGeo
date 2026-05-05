import argparse
import json
from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.eval.model_service import summarize_model_rag_outputs
from minigeo.finetune.adapter_eval import format_sft_adapter_report, reparse_adapter_records
from minigeo.jsonl import read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Reparse saved SFT adapter outputs without calling the model again.")
    parser.add_argument("--input", default="results/sft_adapter_128step_smoke10.jsonl")
    parser.add_argument("--benchmark", default="data/benchmark/minigeo_bench.jsonl")
    parser.add_argument("--output", default="results/sft_adapter_128step_smoke10_reparsed.jsonl")
    parser.add_argument("--report", default="results/sft_adapter_128step_smoke10_reparsed.md")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    report_path = Path(args.report)
    records = read_jsonl(input_path)
    reparsed = reparse_adapter_records(records)
    write_jsonl(output_path, reparsed)

    benchmark_by_id = {row["id"]: row for row in load_benchmark(Path(args.benchmark))}
    rows = [benchmark_by_id[record["id"]] for record in reparsed if record["id"] in benchmark_by_id]
    outputs = {record["id"]: record.get("result", {}) for record in reparsed}
    summary = summarize_model_rag_outputs(rows, outputs)
    summary["thinking_raw_outputs"] = sum(
        1 for record in reparsed
        if "</think>" in str(record.get("result", {}).get("raw_model_output", ""))
        or "<think>" in str(record.get("result", {}).get("raw_model_output", ""))
    )
    report = format_sft_adapter_report(
        adapter_dir=Path(reparsed[0].get("adapter_dir", "")) if reparsed else Path(""),
        summary=summary,
        records_path=output_path,
        dry_run=False,
    )
    report += "\n## Reparse Notes\n\n"
    report += "- 本报告由已有 raw_model_output 离线重解析生成，没有重新调用模型。\n"
    report += f"- thinking_raw_outputs={summary['thinking_raw_outputs']}\n"
    report_path.write_text(report, encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote={output_path}")
    print(f"wrote={report_path}")


if __name__ == "__main__":
    main()
