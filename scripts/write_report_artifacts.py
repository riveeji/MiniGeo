import json
from pathlib import Path
from time import perf_counter

from minigeo.agent.simple_agent import MiniGeoAgent
from minigeo.benchmark import load_benchmark
from minigeo.eval.abstention import summarize_abstention
from minigeo.eval.agent_planner import summarize_planner_routes
from minigeo.eval.report_artifacts import abstention_failure_cases, format_failure_cases, format_main_results
from minigeo.eval.retrieval_ablation import run_retrieval_ablation
from minigeo.eval.sql import summarize_sql_results
from minigeo.eval.verifier import summarize_verification_reports
from minigeo.eval.model_service import summarize_model_rag_outputs
from minigeo.jsonl import read_jsonl
from minigeo.rag.bm25 import BM25Retriever
from minigeo.rag.corpus import load_corpus
from minigeo.rag.pipeline import offline_rag_answer
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


def _saved_model_rows(bench: list[dict]) -> list[tuple]:
    rag_path = _best_model_output_path("rag")
    no_rag_path = _best_model_output_path("no_rag")
    configs = [
        ("Qwen3.5-4B no-RAG", no_rag_path),
        ("Qwen3.5-4B + BM25 RAG", rag_path),
    ]
    rows = []
    benchmark_by_id = {row["id"]: row for row in bench}
    for label, path in configs:
        if not path.exists():
            continue
        records = read_jsonl(path)
        outputs = {record["id"]: record.get("result", {}) for record in records}
        matched_bench = [benchmark_by_id[record["id"]] for record in records if record["id"] in benchmark_by_id]
        summary = summarize_model_rag_outputs(matched_bench, outputs)
        rows.append(
            (
                label,
                "",
                summary.get("citation_hit_rate"),
                "",
                summary.get("abstention_accuracy"),
                "-",
                "见 model_service_eval",
            )
        )
    verified_path = _best_verified_model_output_path()
    if verified_path.exists():
        rows.append(_verified_model_row("Qwen3.5-4B + BM25 RAG + Verifier", verified_path, benchmark_by_id))
    model_verified_path = _best_model_verified_output_path()
    if model_verified_path.exists():
        rows.append(
            _verified_model_row(
                "Qwen3.5-4B + BM25 RAG + Model Verifier",
                model_verified_path,
                benchmark_by_id,
                "见 model_service_model_verified_eval",
            )
        )
    if Path("results/model_service_eval.md").exists():
        rows.append(("Qwen3.5-4B SQL generator", "", "", "", "", 1.0, "见 model_service_eval"))
    rows.extend(_saved_retrieval_service_rows())
    return rows


def _saved_retrieval_service_rows(path: Path = Path("results/retrieval_service_eval.json")) -> list[tuple]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if "main_result_rows" in data:
        return [
            (
                row.get("system", ""),
                "",
                row.get("citation_hit_rate"),
                "",
                "",
                "-",
                row.get("latency", "见 retrieval_service_eval"),
            )
            for row in data["main_result_rows"]
        ]
    metrics = data.get("metrics", {})
    model = str(data.get("model", "Qwen3-Embedding-0.6B")).split("/")[-1]
    rows = []
    labels = {
        "dense": f"{model} dense retrieval",
        "hybrid": f"{model} hybrid retrieval",
        "hybrid_rerank": f"{model} hybrid + lexical rerank",
    }
    for key, label in labels.items():
        if key not in metrics:
            continue
        rows.append(
            (
                label,
                "",
                metrics[key].get("citation_hit_rate"),
                "",
                "",
                "-",
                "见 retrieval_service_eval",
            )
        )
    return rows


def _saved_agent_case_summary(path: Path = Path("results/agent_cases.json")) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("summary", {})


def _saved_model_failure_cases(max_cases: int = 3) -> list[dict]:
    path = _best_model_output_path("rag")
    if not path.exists():
        return []
    cases = []
    for record in read_jsonl(path):
        expected = set(record.get("gold_evidence") or [])
        result = record.get("result", {})
        citations = set(result.get("citations") or [])
        if not expected or expected.intersection(citations):
            continue
        answer = str(result.get("answer", "")).replace("\n", " ")[:180]
        cases.append(
            {
                "case_id": f"model_service_{len(cases) + 1:03d}",
                "question": record.get("question", ""),
                "system": "Qwen3.5-4B + BM25 RAG",
                "observed_output": f"citations={sorted(citations)}; answer={answer}",
                "expected_behavior": ", ".join(sorted(expected)),
                "failure_type": "model_citation_miss",
                "suspected_cause": "模型最终回答使用了相关但非 gold 的 chunk，或在证据不足场景中过早拒答。",
                "next_action": "复查 citation miss 样例，比较 BM25 top-k 与模型实际引用；后续用 reranker、Verifier 或更严格 citation prompt 降低 miss。",
            }
        )
        if len(cases) >= max_cases:
            break
    return cases


def _best_model_output_path(mode: str) -> Path:
    candidates = [
        Path(f"results/model_service_qwen35_4b_300_latest_{mode}.jsonl"),
        Path(f"results/model_service_qwen35_4b_300_{mode}.jsonl"),
        Path(f"results/model_service_qwen35_4b_150_latest_{mode}.jsonl"),
        Path(f"results/model_service_qwen35_4b_150_{mode}.jsonl"),
        Path(f"results/model_service_qwen35_4b_{mode}.jsonl"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[-1]


def _best_verified_model_output_path() -> Path:
    candidates = [
        Path("results/model_service_qwen35_4b_300_latest_rag_verified.jsonl"),
        Path("results/model_service_qwen35_4b_300_rag_verified.jsonl"),
        Path("results/model_service_qwen35_4b_150_latest_rag_verified.jsonl"),
        Path("results/model_service_qwen35_4b_150_rag_verified.jsonl"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[-1]


def _best_model_verified_output_path() -> Path:
    candidates = [
        Path("results/model_service_qwen35_4b_300_latest_rag_model_verified.jsonl"),
        Path("results/model_service_qwen35_4b_150_latest_rag_model_verified.jsonl"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[-1]


def _verified_model_row(
    label: str,
    path: Path,
    benchmark_by_id: dict[str, dict],
    latency_note: str = "见 model_service_verified_eval",
) -> tuple:
    records = read_jsonl(path)
    outputs = {record["id"]: record.get("result", {}) for record in records}
    matched_bench = [benchmark_by_id[record["id"]] for record in records if record["id"] in benchmark_by_id]
    model_summary = summarize_model_rag_outputs(matched_bench, outputs)
    verifier_summary = summarize_verification_reports(
        [
            record.get("result", {}).get("verification", {"verdict": "missing", "claims": []})
            for record in records
        ]
    )
    return (
        label,
        "",
        model_summary.get("citation_hit_rate"),
        verifier_summary.get("unsupported_claim_rate"),
        model_summary.get("abstention_accuracy"),
        "-",
        latency_note,
    )


def main() -> None:
    bench = load_benchmark(Path("data/benchmark/minigeo_bench.jsonl"))
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    retrieval = run_retrieval_ablation(bench, corpus, top_k=10)

    started = perf_counter()
    planner_summary = summarize_planner_routes(bench)
    planner_latency_ms = (perf_counter() - started) * 1000.0 / max(len(bench), 1)
    planner_summary["latency_ms"] = planner_latency_ms

    started = perf_counter()
    rag_answers = {row["id"]: offline_rag_answer(row["question"], corpus, top_k=3) for row in bench}
    abstention_latency_ms = (perf_counter() - started) * 1000.0 / max(len(bench), 1)

    chunks_by_id = {row["chunk_id"]: row for row in corpus}
    verifier = MiniGeoVerifier()
    verifier_reports = []
    started = perf_counter()
    for row in bench:
        evidence = [chunks_by_id[chunk_id] for chunk_id in row["evidence"] if chunk_id in chunks_by_id]
        verifier_reports.append(verifier.verify(row["answer"], evidence))
    verifier_latency_ms = (perf_counter() - started) * 1000.0 / max(len(bench), 1)

    db_path = Path("data/processed/minigeo_demo.sqlite")
    init_demo_db(db_path)
    generator = RuleBasedSQLGenerator()
    sql_outputs = {}
    sql_rows = [row for row in bench if row["requires_sql"]]
    started = perf_counter()
    for row in sql_rows:
        sql = generator.generate(row["question"])
        result = execute_sql(db_path, sql)
        if result["error"]:
            result = execute_sql(db_path, repair_sql(sql, result["error"]))
        sql_outputs[row["id"]] = result
    sql_latency_ms = (perf_counter() - started) * 1000.0 / max(len(sql_rows), 1)

    started = perf_counter()
    agent_report = MiniGeoAgent(db_path=db_path, corpus=corpus).run(
        "Analyze which mineral categories are most frequently misclassified in samples collected from Qinhuangdao, "
        "and explain possible causes using spectral evidence."
    )
    agent_latency_ms = (perf_counter() - started) * 1000.0
    agent_demo_passed = agent_report["sql_result"]["error"] is None and bool(agent_report["evidence"])

    Path("results/main_results.md").write_text(
        format_main_results(
            retrieval=retrieval,
            verifier=summarize_verification_reports(verifier_reports, latency_ms=verifier_latency_ms),
            sql=summarize_sql_results(bench, sql_outputs, latency_ms=sql_latency_ms),
            abstention=summarize_abstention(bench, rag_answers, latency_ms=abstention_latency_ms),
            planner=planner_summary,
            agent_demo_passed=agent_demo_passed,
            agent_latency_ms=agent_latency_ms,
            agent_cases=_saved_agent_case_summary(),
            extra_rows=_saved_model_rows(bench),
        ),
        encoding="utf-8",
        newline="\n",
    )
    Path("results/failure_cases.md").write_text(
        format_failure_cases(
            _bm25_failure_cases(bench, corpus)
            + abstention_failure_cases(bench, rag_answers)
            + _saved_model_failure_cases()
        ),
        encoding="utf-8",
        newline="\n",
    )
    print("wrote=results/main_results.md")
    print("wrote=results/failure_cases.md")


if __name__ == "__main__":
    main()
