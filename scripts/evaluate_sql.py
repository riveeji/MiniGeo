import argparse
import os
from pathlib import Path
import sqlite3
import sys

from minigeo.benchmark import load_benchmark
from minigeo.eval.sql import summarize_sql_results
from minigeo.sql.model_generator import sql_generator_from_env
from minigeo.sql.repair import repair_sql
from minigeo.sql.tools import execute_sql, init_demo_db, schema_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate SQL generation and execution on MiniGeo-Bench SQL items.")
    parser.add_argument("--use-model", action="store_true", help="Use model-backed SQL generator from environment variables.")
    args = parser.parse_args()

    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    db_path = Path("data/processed/minigeo_demo.sqlite")
    init_demo_db(db_path)
    env = dict(os.environ)
    if args.use_model:
        env["MINIGEO_SQL_USE_MODEL"] = "1"
    try:
        generator = sql_generator_from_env(env)
    except ValueError as exc:
        print(f"configuration_error={exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    with sqlite3.connect(db_path) as conn:
        schema = schema_text(conn)
    outputs = {}
    for row in bench:
        if not row["requires_sql"]:
            continue
        try:
            sql = generator.generate(row["question"], schema=schema)
        except TypeError:
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
