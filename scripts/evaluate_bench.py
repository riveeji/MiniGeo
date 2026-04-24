from pathlib import Path

from minigeo.benchmark import benchmark_summary, load_benchmark


def main() -> None:
    path = Path("data/benchmark/minigeo_bench.jsonl")
    rows = load_benchmark(path)
    summary = benchmark_summary(rows)
    for key, value in summary.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()

