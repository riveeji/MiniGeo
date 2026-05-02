from collections import Counter
from typing import Any

from minigeo.eval.model_failure_analysis import _classify_failure


REVIEW_FIELDS = [
    "id",
    "category",
    "question",
    "gold_evidence",
    "citations",
    "retrieved_evidence",
    "answer",
    "review_decision",
    "suggested_evidence",
    "reviewer_note",
]


def build_failure_review_rows(
    records: list[dict[str, Any]],
    categories: set[str] | None = None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for record in records:
        gold = set(record.get("gold_evidence") or [])
        result = record.get("result", {})
        citations = set(result.get("citations") or [])
        if not gold or gold.intersection(citations):
            continue
        category = _classify_failure(gold, result)
        if categories is not None and category not in categories:
            continue
        rows.append(
            {
                "id": str(record.get("id", "")),
                "category": category,
                "question": str(record.get("question", "")),
                "gold_evidence": ", ".join(sorted(gold)),
                "citations": ", ".join(sorted(citations)),
                "retrieved_evidence": ", ".join(
                    str(row.get("chunk_id", "")) for row in result.get("evidence", [])
                ),
                "answer": str(result.get("answer", "")).replace("\n", " "),
                "review_decision": "",
                "suggested_evidence": "",
                "reviewer_note": "",
            }
        )
    return rows


def format_failure_review_markdown(rows: list[dict[str, str]]) -> str:
    counts = Counter(row["category"] for row in rows)
    lines = [
        "# MiniGeo 失败样例人工抽检表",
        "",
        "本文件用于人工判断 citation miss 的真实原因。CSV 中的 `review_decision` 建议只填写下列值之一：",
        "",
        "- `model_error`：模型引用错误，gold evidence 正确。",
        "- `label_expand`：模型引用的 chunk 也能支撑答案，应扩充 benchmark evidence label。",
        "- `retrieval_error`：检索结果缺少必要证据，应改检索或语料。",
        "- `ambiguous`：题目、答案或证据边界不清，需要重写样例。",
        "",
        "## 分类数量",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]
    for category, count in sorted(counts.items()):
        lines.append(f"| {category} | {count} |")
    lines.extend(
        [
            "",
            "## 抽检样例",
            "",
            "| ID | Category | Question | Gold | Citations |",
            "|---|---|---|---|---|",
        ]
    )
    for row in rows[:20]:
        lines.append(
            "| "
            f"{row['id']} | "
            f"{row['category']} | "
            f"{_escape_table(row['question'])} | "
            f"{_escape_table(row['gold_evidence'])} | "
            f"{_escape_table(row['citations']) or 'None'} |"
        )
    lines.extend(
        [
            "",
            "## 使用方法",
            "",
            "1. 打开配套 CSV，逐行检查 `answer` 是否被 `citations` 支撑。",
            "2. 如果引用 chunk 可以支撑答案，在 `review_decision` 填 `label_expand`，并把应加入的 chunk 写入 `suggested_evidence`。",
            "3. 如果引用 chunk 不能支撑答案，在 `review_decision` 填 `model_error`。",
            "4. 如果 gold 没进 `retrieved_evidence`，优先填 `retrieval_error`。",
            "",
        ]
    )
    return "\n".join(lines)


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
