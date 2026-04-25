from pathlib import Path

from minigeo.agent.simple_agent import MiniGeoAgent
from minigeo.benchmark import load_benchmark
from minigeo.eval.report_artifacts import format_failure_cases, format_main_results
from minigeo.eval.retrieval_ablation import run_retrieval_ablation
from minigeo.eval.sql import summarize_sql_results
from minigeo.eval.verifier import summarize_verification_reports
from minigeo.rag.bm25 import BM25Retriever
from minigeo.rag.corpus import load_corpus
from minigeo.sql.generator import RuleBasedSQLGenerator
from minigeo.sql.repair import repair_sql
from minigeo.sql.tools import execute_sql, init_demo_db
from minigeo.verifier.verifier import MiniGeoVerifier


def _bm25_failure_cases(bench: list[dict], corpus: list[dict], max_cases: int = 5) -> list[dict]:
    retriever = BM25Retriever(corpus)
    cases = []
    for row in bench:
        expected = set(row.get("evidence") or [])
        if not expected:
            continue
        retrieved = retriever.search(row["question"], top_k=10)
        retrieved_ids = [item["chunk_id"] for item in retrieved]
        if expected.intersection(retrieved_ids):
            continue
        cases.append(
            {
                "case_id": f"retrieval_{len(cases) + 1:03d}",
                "question": row["question"],
                "system": "BM25 RAG baseline",
                "observed_output": ", ".join(retrieved_ids[:5]),
                "expected_behavior": ", ".join(sorted(expected)),
                "failure_type": "retrieval_miss",
                "suspected_cause": "tokenizer、同义词或语料覆盖不足",
                "next_action": "补充同义词、改进 query rewrite，或增加对应公开资料 chunk。",
            }
        )
        if len(cases) >= max_cases:
            break
    return cases


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

    agent_report = MiniGeoAgent(db_path=db_path, corpus=corpus).run(
        "Analyze which mineral categories are most frequently misclassified in samples collected from Qinhuangdao, "
        "and explain possible causes using spectral evidence."
    )
    agent_demo_passed = agent_report["sql_result"]["error"] is None and bool(agent_report["evidence"])

    Path("results/main_results.md").write_text(
        format_main_results(
            retrieval=retrieval,
            verifier=summarize_verification_reports(verifier_reports),
            sql=summarize_sql_results(bench, sql_outputs),
            agent_demo_passed=agent_demo_passed,
        ),
        encoding="utf-8",
        newline="\n",
    )
    Path("results/failure_cases.md").write_text(
        format_failure_cases(_bm25_failure_cases(bench, corpus)),
        encoding="utf-8",
        newline="\n",
    )
    print("wrote=results/main_results.md")
    print("wrote=results/failure_cases.md")


if __name__ == "__main__":
    main()
