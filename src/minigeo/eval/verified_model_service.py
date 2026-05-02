from typing import Any

from minigeo.eval.model_service import summarize_model_rag_outputs
from minigeo.eval.verifier import summarize_verification_reports
from minigeo.rag.verified_model_rag import Verifier, verify_rag_answer


def verify_saved_model_records(
    records: list[dict[str, Any]],
    verifier: Verifier | None = None,
) -> list[dict[str, Any]]:
    verified_records = []
    for record in records:
        verified = dict(record)
        verified["result"] = verify_rag_answer(dict(record.get("result", {})), verifier=verifier)
        verified_records.append(verified)
    return verified_records


def summarize_verified_model_records(
    benchmark_rows: list[dict[str, Any]],
    verified_records: list[dict[str, Any]],
) -> dict[str, Any]:
    outputs = {record["id"]: record.get("result", {}) for record in verified_records}
    return {
        "model": summarize_model_rag_outputs(benchmark_rows, outputs),
        "verifier": summarize_verification_reports(
            [
                record.get("result", {}).get("verification", {"verdict": "missing", "claims": []})
                for record in verified_records
            ]
        ),
    }


def format_verified_model_report(
    model_summary: dict[str, Any],
    verifier_summary: dict[str, Any],
    output_path: str,
    verifier_mode: str = "heuristic",
) -> str:
    return "\n".join(
        [
            "# MiniGeo RAG + Verifier 离线评测",
            "",
            "本报告基于已保存的模型 RAG 输出离线生成，不会再次调用模型服务。",
            "",
            f"- output：`{output_path}`",
            f"- verifier_mode：{verifier_mode}",
            f"- items：{model_summary.get('items', 0)}",
            f"- citation_hit_rate：{model_summary.get('citation_hit_rate', 0.0):.3f}",
            f"- abstention_accuracy：{model_summary.get('abstention_accuracy', 0.0):.3f}",
            f"- request_errors：{model_summary.get('request_errors', 0)}",
            f"- unsupported_claim_rate：{verifier_summary.get('unsupported_claim_rate', 0.0):.3f}",
            "",
            "## Verifier Verdicts",
            "",
            "| Verdict | Count |",
            "|---|---:|",
            *[
                f"| {verdict} | {count} |"
                for verdict, count in sorted(verifier_summary.get("verdicts", {}).items())
            ],
            "",
        ]
    )
