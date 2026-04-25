from pathlib import Path

from minigeo.benchmark import benchmark_summary, load_benchmark
from minigeo.eval.local_summary import format_markdown_summary
from minigeo.eval.retrieval_ablation import run_retrieval_ablation
from minigeo.eval.sql import summarize_sql_results
from minigeo.eval.verifier import summarize_verification_reports
from minigeo.rag.corpus import load_corpus
from minigeo.sql.generator import RuleBasedSQLGenerator
from minigeo.sql.repair import repair_sql
from minigeo.sql.tools import execute_sql, init_demo_db
from minigeo.verifier.verifier import MiniGeoVerifier


def main() -> None:
    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    retrieval = run_retrieval_ablation(bench, corpus, top_k=10)

    chunks_by_id = {row["chunk_id"]: row for row in corpus}
    verifier = MiniGeoVerifier()
    verifier_reports = []
    for row in bench:
        evidence = [chunks_by_id[chunk_id] for chunk_id in row["evidence"] if chunk_id in chunks_by_id]
        verifier_reports.append(verifier.verify(row["answer"], evidence))

    db_path = Path("data/processed/minigeo_demo.sqlite")
    init_demo_db(db_path)
    generator = RuleBasedSQLGenerator()
    sql_outputs = {}
    for row in bench:
        if not row["requires_sql"]:
            continue
        sql = generator.generate(row["question"])
        result = execute_sql(db_path, sql)
        if result["error"]:
            result = execute_sql(db_path, repair_sql(sql, result["error"]))
        sql_outputs[row["id"]] = result

    markdown = format_markdown_summary(
        benchmark_summary(bench),
        retrieval,
        summarize_verification_reports(verifier_reports),
        summarize_sql_results(bench, sql_outputs),
    )
    output = Path("results/local_eval_summary.md")
    output.write_text(markdown, encoding="utf-8", newline="\n")
    print(f"wrote={output}")


if __name__ == "__main__":
    main()

