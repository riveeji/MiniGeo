import argparse
import json
from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.eval.model_output_quality import analyze_model_outputs, format_model_output_quality_markdown
from minigeo.jsonl import read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit saved model-service outputs without calling the model.")
    parser.add_argument("--benchmark", default="data/benchmark/minigeo_bench.jsonl")
    parser.add_argument("--rag", default="results/model_service_qwen35_4b_rag.jsonl")
    parser.add_argument("--no-rag", default="results/model_service_qwen35_4b_no_rag.jsonl")
    parser.add_argument("--output", default="results/model_output_quality.md")
    args = parser.parse_args()

    benchmark = load_benchmark(Path(args.benchmark))
    inputs = {
        "rag": Path(args.rag),
        "no-rag": Path(args.no_rag),
    }
    summaries = {}
    for mode, path in inputs.items():
        records = read_jsonl(path)
        summaries[mode] = analyze_model_outputs(records, benchmark)
    output = Path(args.output)
    output.write_text(format_model_output_quality_markdown(summaries), encoding="utf-8", newline="\n")
    print(json.dumps(summaries, ensure_ascii=False))
    print(f"wrote={output}")


if __name__ == "__main__":
    main()
