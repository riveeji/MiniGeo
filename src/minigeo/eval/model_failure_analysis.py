from collections import Counter
from typing import Any


def analyze_rag_failures(records: list[dict[str, Any]], max_examples: int = 12) -> dict[str, Any]:
    categories: Counter[str] = Counter()
    examples: list[dict[str, Any]] = []
    citation_misses = 0
    for record in records:
        gold = set(record.get("gold_evidence") or [])
        result = record.get("result", {})
        citations = set(result.get("citations") or [])
        if not gold or gold.intersection(citations):
            continue
        citation_misses += 1
        category = _classify_failure(gold, result)
        categories[category] += 1
        if len(examples) < max_examples:
            examples.append(
                {
                    "id": record.get("id", ""),
                    "category": category,
                    "question": record.get("question", ""),
                    "gold": sorted(gold),
                    "citations": sorted(citations),
                    "retrieved": [row.get("chunk_id", "") for row in result.get("evidence", [])],
                    "answer": str(result.get("answer", "")).replace("\n", " ")[:240],
                }
            )
    return {
        "total_records": len(records),
        "citation_misses": citation_misses,
        "citation_miss_rate": citation_misses / max(len(records), 1),
        "categories": dict(categories),
        "examples": examples,
    }


def format_failure_analysis_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# MiniGeo 模型失败分析",
        "",
        "本报告基于已保存的 Qwen3.5-4B + BM25 RAG 输出离线生成，不会再次调用模型。",
        "",
        f"- total_records：{report['total_records']}",
        f"- citation_misses：{report['citation_misses']}",
        f"- citation_miss_rate：{report.get('citation_miss_rate', 0.0):.3f}",
        "",
        "## 分类统计",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]
    for category, count in sorted(report.get("categories", {}).items()):
        lines.append(f"| {category} | {count} |")
    lines.extend(["", "## 样例", ""])
    for example in report.get("examples", []):
        lines.extend(
            [
                "```text",
                f"id: {example['id']}",
                f"category: {example['category']}",
                f"question: {example['question']}",
                f"gold: {', '.join(example['gold'])}",
                f"citations: {', '.join(example['citations']) or 'None'}",
                f"retrieved: {', '.join(example['retrieved']) or 'None'}",
                f"answer: {example['answer']}",
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## 下一步处理建议",
            "",
            "1. 先处理 `model_cited_other`：gold chunk 已在 prompt 中但模型引用了其他 chunk，优先收紧 citation prompt，并在 Verifier 中检查最终引用是否逐条支撑回答。",
            "2. 再处理 `model_cited_neighbor`：这类多半是 chunk 粒度或 gold label 过窄，适合人工抽检后决定是否扩充 evidence label。",
            "3. 单独处理 `model_abstained_with_gold`：gold evidence 已进入 prompt 仍拒答，说明拒答阈值或 JSON 解析后的 abstained 字段需要调参。",
            "4. 最后处理 `retrieval_gold_missing`：数量少但是真检索问题，应补 query expansion、reranker 或 corpus 覆盖。",
            "",
            "## 分类解释",
            "",
            "- `retrieval_gold_missing`：gold evidence 没有进入 RAG prompt，主要应改检索或 evidence label。",
            "- `model_abstained_with_gold`：gold evidence 已进入 prompt，但模型仍拒答，主要应改 prompt 或拒答策略。",
            "- `model_cited_neighbor`：模型引用了同一文档的相邻 chunk，可能是 gold label 过窄或 citation policy 不够严格。",
            "- `model_cited_other`：模型引用了非 gold、非相邻 chunk，优先检查 reranker、prompt 和 benchmark 标注。",
            "",
        ]
    )
    return "\n".join(lines)


def _classify_failure(gold: set[str], result: dict[str, Any]) -> str:
    retrieved = result.get("evidence", [])
    retrieved_ids = {str(row.get("chunk_id", "")) for row in retrieved}
    citations = {str(value) for value in result.get("citations", [])}
    if not gold.intersection(retrieved_ids):
        return "retrieval_gold_missing"
    if result.get("abstained"):
        return "model_abstained_with_gold"
    gold_docs = {_doc_id(chunk_id) for chunk_id in gold}
    citation_docs = {_doc_id(chunk_id) for chunk_id in citations}
    if gold_docs.intersection(citation_docs):
        return "model_cited_neighbor"
    return "model_cited_other"


def _doc_id(chunk_id: str) -> str:
    return chunk_id.split("#", 1)[0]
