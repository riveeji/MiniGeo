from collections import Counter
from typing import Any

from minigeo.rag.bm25 import BM25Retriever
from minigeo.rag.dense import DenseRetriever
from minigeo.rag.hybrid import hybrid_search
from minigeo.rag.reranker import LexicalReranker
from minigeo.rag.tokenizer import tokenize


def collect_retrieval_outputs(
    benchmark_rows: list[dict[str, Any]],
    corpus_rows: list[dict[str, Any]],
    top_k: int = 10,
) -> dict[str, dict[str, list[str]]]:
    bm25 = BM25Retriever(corpus_rows)
    dense = DenseRetriever(corpus_rows)
    reranker = LexicalReranker()
    outputs: dict[str, dict[str, list[str]]] = {"bm25": {}, "dense": {}, "hybrid": {}, "hybrid_rerank": {}}
    for row in benchmark_rows:
        question = row["question"]
        outputs["bm25"][row["id"]] = [item["chunk_id"] for item in bm25.search(question, top_k=top_k)]
        outputs["dense"][row["id"]] = [item["chunk_id"] for item in dense.search(question, top_k=top_k)]
        hybrid_candidates = hybrid_search(
            question,
            corpus_rows,
            top_k=max(top_k * 2, top_k),
            bm25_retriever=bm25,
            dense_retriever=dense,
        )
        outputs["hybrid"][row["id"]] = [item["chunk_id"] for item in hybrid_candidates[:top_k]]
        outputs["hybrid_rerank"][row["id"]] = [
            item["chunk_id"] for item in reranker.rerank(question, hybrid_candidates, top_k=top_k)
        ]
    return outputs


def analyze_retrieval_failures(
    benchmark_rows: list[dict[str, Any]],
    corpus_rows: list[dict[str, Any]],
    outputs: dict[str, dict[str, list[str]]],
    top_k: int = 10,
    max_cases_per_system: int = 10,
) -> dict[str, Any]:
    corpus_by_id = {row["chunk_id"]: row for row in corpus_rows}
    rows_with_evidence = [row for row in benchmark_rows if row.get("evidence")]
    cases: list[dict[str, Any]] = []
    summary: dict[str, dict[str, Any]] = {}
    for system, retrieved_by_id in outputs.items():
        categories: Counter[str] = Counter()
        misses = 0
        system_cases = 0
        for row in rows_with_evidence:
            expected = list(row.get("evidence") or [])
            retrieved = list(retrieved_by_id.get(row["id"], []))[:top_k]
            if set(expected) & set(retrieved):
                continue
            misses += 1
            category = _classify_failure(row, expected, retrieved, corpus_by_id, outputs, system)
            categories[category] += 1
            if system_cases >= max_cases_per_system:
                continue
            system_cases += 1
            cases.append(
                {
                    "system": system,
                    "id": row["id"],
                    "question": row["question"],
                    "expected_evidence": expected,
                    "retrieved_ids": retrieved,
                    "category": category,
                    "suspected_cause": _suspected_cause(category),
                    "next_action": _next_action(category),
                }
            )
        total = len(rows_with_evidence)
        summary[system] = {
            "items": total,
            "misses": misses,
            "miss_rate": misses / max(total, 1),
            "categories": dict(categories),
        }
    return {"summary": summary, "cases": cases}


def _classify_failure(
    row: dict[str, Any],
    expected: list[str],
    retrieved: list[str],
    corpus_by_id: dict[str, dict[str, Any]],
    outputs: dict[str, dict[str, list[str]]],
    system: str,
) -> str:
    if any(chunk_id not in corpus_by_id for chunk_id in expected):
        return "gold_evidence_missing_from_corpus"
    if system == "hybrid_rerank" and set(expected) & set(outputs.get("hybrid", {}).get(row["id"], [])):
        return "reranker_demoted_gold"
    expected_docs = {corpus_by_id[chunk_id].get("doc_id") for chunk_id in expected if chunk_id in corpus_by_id}
    retrieved_docs = {corpus_by_id[chunk_id].get("doc_id") for chunk_id in retrieved if chunk_id in corpus_by_id}
    if expected_docs & retrieved_docs:
        return "evidence_label_narrow"
    expected_topics = {corpus_by_id[chunk_id].get("topic") for chunk_id in expected if chunk_id in corpus_by_id}
    retrieved_topics = {corpus_by_id[chunk_id].get("topic") for chunk_id in retrieved if chunk_id in corpus_by_id}
    if expected_topics and expected_topics & retrieved_topics:
        return "same_topic_wrong_chunk"
    expected_text = " ".join(str(corpus_by_id[chunk_id].get("text", "")) for chunk_id in expected if chunk_id in corpus_by_id)
    if not set(tokenize(row["question"])) & set(tokenize(expected_text)):
        return "tokenizer_or_query_gap"
    return "retrieval_gold_missing"


def _suspected_cause(category: str) -> str:
    return {
        "gold_evidence_missing_from_corpus": "benchmark evidence 指向了当前 corpus 中不存在的 chunk。",
        "reranker_demoted_gold": "reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。",
        "evidence_label_narrow": "检索到了同一文档的相关 chunk，但 benchmark 只标了更窄的 gold chunk。",
        "same_topic_wrong_chunk": "检索到了同 topic 的 chunk，但排序没有命中精确证据。",
        "tokenizer_or_query_gap": "问题文本和 gold evidence 的可检索词重叠较弱，可能需要 query rewrite 或同义词扩展。",
        "retrieval_gold_missing": "检索排序未把 gold evidence 放入 top-k。",
    }.get(category, "未分类检索失败。")


def _next_action(category: str) -> str:
    return {
        "gold_evidence_missing_from_corpus": "修复 benchmark evidence id 或补齐 corpus chunk。",
        "reranker_demoted_gold": "检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。",
        "evidence_label_narrow": "人工复核 retrieved chunk 是否也能支撑答案；若能支撑，应扩充 evidence label。",
        "same_topic_wrong_chunk": "补充更细粒度 query expansion、chunk metadata 或 reranker 特征。",
        "tokenizer_or_query_gap": "补充中文/英文同义词、矿物别名和光谱峰位 query rewrite。",
        "retrieval_gold_missing": "扩充语料、改进检索融合权重或提高 candidate_k。",
    }.get(category, "人工复核该失败样例。")


def format_retrieval_failure_report(report: dict[str, Any]) -> str:
    lines = [
        "# MiniGeo 检索失败分析",
        "",
        "本报告分析 evidence-labeled benchmark 上各检索系统的 top-k miss case，用于区分 tokenizer、语料、evidence label 和 reranker 排序问题。",
        "",
        "## 汇总",
        "",
        "| System | Items | Misses | Miss Rate | Categories |",
        "|---|---:|---:|---:|---|",
    ]
    for system, metrics in report["summary"].items():
        categories = ", ".join(f"{key}={value}" for key, value in sorted(metrics["categories"].items())) or "-"
        lines.append(
            f"| {system} | {metrics['items']} | {metrics['misses']} | {metrics['miss_rate']:.3f} | {categories} |"
        )
    lines.extend(["", "## 样例", ""])
    if not report["cases"]:
        lines.extend(["当前 top-k 没有检索 miss case。", ""])
        return "\n".join(lines)
    for case in report["cases"]:
        lines.extend(
            [
                "```text",
                f"system: {case['system']}",
                f"id: {case['id']}",
                f"question: {case['question']}",
                f"expected_evidence: {', '.join(case['expected_evidence'])}",
                f"retrieved_ids: {', '.join(case['retrieved_ids'])}",
                f"category: {case['category']}",
                f"suspected_cause: {case['suspected_cause']}",
                f"next_action: {case['next_action']}",
                "```",
                "",
            ]
        )
    return "\n".join(lines)
