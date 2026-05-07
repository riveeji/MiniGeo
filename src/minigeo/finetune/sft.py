import json
from typing import Any


def _compact_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _evidence_chunks(row: dict[str, Any], corpus_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    chunks = []
    for chunk_id in row.get("evidence") or []:
        chunk = corpus_by_id.get(str(chunk_id))
        if chunk:
            chunks.append(chunk)
    return chunks


def _format_evidence_block(chunks: list[dict[str, Any]]) -> str:
    return "\n".join(f"[{chunk['chunk_id']}] {_compact_text(chunk['text'])}" for chunk in chunks)


def _citation_answer(chunks: list[dict[str, Any]]) -> str:
    first = chunks[0]
    text = _compact_text(first["text"])
    citation = first["chunk_id"]
    return f"根据证据，{text} [{citation}]。"


def _json_output(answer: str, citations: list[str] | None = None, abstained: bool = False, confidence: float = 0.7) -> str:
    return json.dumps(
        {
            "answer": _compact_text(answer),
            "citations": citations or [],
            "abstained": abstained,
            "confidence": confidence,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _instruction(base: str) -> str:
    return (
        f"{base}\n"
        "Output exactly one JSON object and then stop. "
        "Do not output markdown, schema examples, <think>, </think>, hidden reasoning, or multiple JSON objects. "
        "The JSON keys must be answer, citations, abstained, confidence. "
        "If the answer says evidence is insufficient, abstained must be true and confidence must be 0.0."
    )


def build_sft_examples(benchmark_rows: list[dict[str, Any]], corpus_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    corpus_by_id = {str(chunk["chunk_id"]): chunk for chunk in corpus_rows}

    for idx, chunk in enumerate(corpus_rows, start=1):
        examples.append(
            {
                "id": f"sft_evidence_{idx:04d}",
                "instruction": "根据给定证据写一个简短、可引用的地学事实摘要。",
                "input": f"[{chunk['chunk_id']}] {chunk['text']}",
                "output": _json_output(
                    f"该证据 chunk 可用于支持与 {chunk.get('topic', '地学')} 相关的回答。",
                    citations=[chunk["chunk_id"]],
                    abstained=False,
                    confidence=0.7,
                ),
                "task_type": "evidence_summary",
            }
        )

    refusal_idx = 1
    sql_idx = 1
    qa_idx = 1
    rewrite_idx = 1
    for row in benchmark_rows:
        chunks = _evidence_chunks(row, corpus_by_id)
        if chunks:
            selected_chunks = chunks[:3]
            evidence_block = _format_evidence_block(selected_chunks)
            question = _compact_text(row["question"])
            examples.append(
                {
                    "id": f"sft_evidence_qa_{qa_idx:04d}",
                    "instruction": "根据问题和证据，用一句中文回答；必须包含证据引用，不能添加证据外事实。",
                    "input": f"Question: {question}\nEvidence:\n{evidence_block}",
                    "output": _json_output(
                        _citation_answer(selected_chunks),
                        citations=[chunk["chunk_id"] for chunk in selected_chunks],
                        abstained=False,
                        confidence=0.8,
                    ),
                    "task_type": "evidence_qa",
                }
            )
            qa_idx += 1
            examples.append(
                {
                    "id": f"sft_verification_{rewrite_idx:04d}",
                    "instruction": "将不可靠回答改写为受证据约束的回答；证据不足时拒答。",
                    "input": (
                        f"Question: {question}\n"
                        f"Unverified answer: 这个问题可以直接给出完整结论。\n"
                        f"Evidence:\n{evidence_block}"
                    ),
                    "output": _json_output(
                        f"证据仅支持：{_citation_answer(selected_chunks)}除这些证据外，不应给出更多确定结论。",
                        citations=[chunk["chunk_id"] for chunk in selected_chunks],
                        abstained=False,
                        confidence=0.75,
                    ),
                    "task_type": "verification_rewrite",
                }
            )
            rewrite_idx += 1

        if row.get("answerable") is False:
            examples.append(
                {
                    "id": f"sft_refusal_{refusal_idx:04d}",
                    "instruction": "当证据不足时，用简短中文拒答，不要编造事实。",
                    "input": row["question"],
                    "output": _json_output(
                        "当前证据不足，无法给出可靠结论；需要补充可验证的来源或样本记录。",
                        citations=[],
                        abstained=True,
                        confidence=0.0,
                    ),
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
                    "output": _json_output(
                        f"SQL_INTENT: {row.get('expected_sql_intent') or '根据 schema 生成只读查询'}",
                        citations=[],
                        abstained=False,
                        confidence=0.8,
                    ),
                    "task_type": "sql_format",
                }
            )
            sql_idx += 1
    for example in examples:
        example["instruction"] = _instruction(str(example["instruction"]))
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
