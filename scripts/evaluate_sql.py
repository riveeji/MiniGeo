from pathlib import Path

from minigeo.benchmark import load_benchmark
from minigeo.eval.sql import summarize_sql_results
from minigeo.sql.generator import RuleBasedSQLGenerator
from minigeo.sql.repair import repair_sql
from minigeo.sql.tools import execute_sql, init_demo_db


def main() -> None:
    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    db_path = Path("data/processed/minigeo_demo.sqlite")
    init_demo_db(db_path)
    generator = RuleBasedSQLGenerator()
    outputs = {}
    for row in bench:
        if not row["requires_sql"]:
            continue
        sql = generator.generate(row["question"])
        result = execute_sql(db_path, sql)
        if result["error"]:
            repaired = repair_sql(sql, result["error"])
            repaired_result = execute_sql(db_path, repaired)
            repaired_result["original_sql"] = sql
            repaired_result["repaired_sql"] = repaired
            outputs[row["id"]] = repaired_result
        else:
            outputs[row["id"]] = result
    summary = summarize_sql_results(bench, outputs)
    for key, value in summary.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()

