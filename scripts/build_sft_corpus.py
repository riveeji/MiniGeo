from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.finetune.sft import build_sft_examples, find_reference_answer_leaks
from minigeo.jsonl import write_jsonl
from minigeo.rag.corpus import load_corpus


def main() -> None:
    benchmark = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    examples = build_sft_examples(benchmark, corpus)
    leaks = find_reference_answer_leaks(examples, benchmark)
    if leaks:
        raise SystemExit(f"reference_answer_leaks={leaks}")
    output = Path("data/processed/sft_corpus.jsonl")
    write_jsonl(output, examples)
    print(f"items={len(examples)}")
    print(f"output={output}")
    print("reference_answer_leaks=[]")


if __name__ == "__main__":
    main()

