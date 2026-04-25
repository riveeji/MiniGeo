from typing import Any


def build_sft_examples(benchmark_rows: list[dict[str, Any]], corpus_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for idx, chunk in enumerate(corpus_rows, start=1):
        examples.append(
            {
                "id": f"sft_evidence_{idx:04d}",
                "instruction": "根据给定证据写一个简短、可引用的地学事实摘要。",
                "input": f"[{chunk['chunk_id']}] {chunk['text']}",
                "output": f"该证据 chunk 可用于支持与 {chunk.get('topic', '地学')} 相关的回答，引用为 [{chunk['chunk_id']}]。",
                "task_type": "evidence_summary",
            }
        )

    refusal_idx = 1
    sql_idx = 1
    for row in benchmark_rows:
        if row.get("answerable") is False:
            examples.append(
                {
                    "id": f"sft_refusal_{refusal_idx:04d}",
                    "instruction": "当证据不足时，用简短中文拒答，不要编造事实。",
                    "input": row["question"],
                    "output": "当前证据不足，无法给出可靠结论；需要补充可验证的来源或样本记录。",
                    "task_type": "refusal",
                }
            )
            refusal_idx += 1
        if row.get("requires_sql"):
            examples.append(
                {
                    "id": f"sft_sql_{sql_idx:04d}",
                    "instruction": "把地学数据库问题改写为 SQL 查询意图，不要输出自然语言结论。",
                    "input": row["question"],
                    "output": f"SQL_INTENT: {row.get('expected_sql_intent') or '根据 schema 生成只读查询'}",
                    "task_type": "sql_format",
                }
            )
            sql_idx += 1
    return examples


def find_reference_answer_leaks(examples: list[dict[str, Any]], benchmark_rows: list[dict[str, Any]]) -> list[str]:
    reference_answers = {
        str(row.get("answer", "")).strip()
        for row in benchmark_rows
        if str(row.get("answer", "")).strip()
    }
    leaks = []
    for example in examples:
        output = str(example.get("output", "")).strip()
        if output in reference_answers:
            leaks.append(example["id"])
    return leaks

