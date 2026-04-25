from pathlib import Path
from time import perf_counter

from minigeo.agent.planner import plan_agent_tools
from minigeo.benchmark import load_benchmark
from minigeo.eval.agent_planner import summarize_planner_routes


def main() -> None:
    rows = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    started = perf_counter()
    for row in rows:
        plan_agent_tools(row["question"])
    latency_ms = (perf_counter() - started) * 1000.0 / max(len(rows), 1)
    summary = summarize_planner_routes(rows, latency_ms=latency_ms)
    for key, value in summary.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
