from collections import Counter
from typing import Any


INTERCEPTION_FIELDS = [
    "id",
    "question",
    "verdict",
    "unverified_answer",
    "final_answer",
    "unsupported_claims",
    "gold_evidence",
    "retrieved_evidence",
    "review_decision",
    "reviewer_note",
]


def build_interception_rows(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for record in records:
        result = record.get("result", {})
        if result.get("verifier_action") != "abstained":
            continue
        verification = result.get("verification", {})
        rows.append(
            {
                "id": str(record.get("id", "")),
                "question": str(record.get("question", "")),
                "verdict": str(verification.get("verdict", "")),
                "unverified_answer": str(result.get("unverified_answer", "")).replace("\n", " "),
                "final_answer": str(result.get("answer", "")).replace("\n", " "),
                "unsupported_claims": "; ".join(_unsupported_claims(verification)),
                "gold_evidence": ", ".join(str(item) for item in record.get("gold_evidence", [])),
                "retrieved_evidence": ", ".join(
                    str(row.get("chunk_id", "")) for row in result.get("evidence", [])
                ),
                "review_decision": "",
                "reviewer_note": "",
            }
        )
    return rows


def format_interception_markdown(rows: list[dict[str, str]]) -> str:
    counts = Counter(row["verdict"] for row in rows)
    lines = [
        "# MiniGeo Verifier 拦截样例",
        "",
        "本文件用于人工判断 Verifier 拦截是否合理。CSV 中的 `review_decision` 建议只填写下列值之一：",
        "",
        "- `correct_reject`：Verifier 正确拦截，原始回答确实未被证据充分支持。",
        "- `false_reject`：Verifier 误杀，原始回答其实被证据支持。",
        "- `claim_split_error`：claim 抽取过碎或抽错，导致误判。",
        "- `needs_model_verifier`：本地 heuristic 不够，需要模型辅助 Verifier 复判。",
        "",
        "## Verdict 数量",
        "",
        "| Verdict | Count |",
        "|---|---:|",
    ]
    for verdict, count in sorted(counts.items()):
        lines.append(f"| {verdict} | {count} |")
    lines.extend(
        [
            "",
            "## 拦截样例",
            "",
            "| ID | Verdict | Question | Unsupported Claims |",
            "|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            f"{row['id']} | "
            f"{row['verdict']} | "
            f"{_escape_table(row['question'])} | "
            f"{_escape_table(row['unsupported_claims']) or 'None'} |"
        )
    lines.extend(
        [
            "",
            "## 使用方法",
            "",
            "1. 对照 `unverified_answer`、`unsupported_claims` 和 `retrieved_evidence`。",
            "2. 如果原始回答确实没有充分证据，填 `correct_reject`。",
            "3. 如果证据其实支持原始回答，填 `false_reject` 或 `claim_split_error`。",
            "4. 如果规则 Verifier 难以判断，填 `needs_model_verifier`，后续在 A100 上用模型辅助 Verifier 复判。",
            "",
        ]
    )
    return "\n".join(lines)


def _unsupported_claims(verification: dict[str, Any]) -> list[str]:
    claims = []
    for claim in verification.get("claims", []):
        if claim.get("status") != "supported":
            claims.append(str(claim.get("claim", "")))
    return [claim for claim in claims if claim]


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
