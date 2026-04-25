import re
from typing import Any

from minigeo.rag.bm25 import BM25Retriever

_SAMPLE_ID_RE = re.compile(r"\b[A-Z]{2,}[A-Z0-9-]*\d+[A-Z0-9-]*\b")


def assemble_evidence_prompt(question: str, evidence: list[dict[str, Any]]) -> str:
    chunks = "\n".join(f"[{row['chunk_id']}] {row['text']}" for row in evidence)
    return (
        "Answer the geoscience question using only the evidence below. "
        "If evidence is insufficient, refuse briefly and say evidence is insufficient. "
        "Cite chunk ids in brackets.\n\n"
        f"Question: {question}\n\nEvidence:\n{chunks}\n\nAnswer:"
    )


def retrieve_with_bm25(question: str, corpus: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
    return BM25Retriever(corpus).search(question, top_k=top_k)


def _should_abstain(question: str, evidence: list[dict[str, Any]]) -> bool:
    if not evidence or all(row.get("score", 0.0) <= 0 for row in evidence):
        return True
    evidence_text = "\n".join(str(row.get("text", "")) for row in evidence)
    sample_ids = _SAMPLE_ID_RE.findall(question)
    if sample_ids and any(sample_id not in evidence_text for sample_id in sample_ids):
        return True
    insufficient_patterns = [
        "检索不到证据",
        "没有证据",
        "证据不足",
        "没有某个样本",
        "当前资料库能否确定样本",
    ]
    if any(pattern in question for pattern in insufficient_patterns):
        return True
    coverage_patterns = [
        ("资料库是否包含", "样本"),
        ("资料库是否包含", "拉曼峰"),
        ("本语料库", "红外峰"),
        ("本语料库", "所有"),
        ("所有红外峰", ""),
    ]
    if any(left in question and (not right or right in question) for left, right in coverage_patterns):
        return True
    return False


def _abstention_answer() -> dict[str, Any]:
    return {
        "answer": "当前证据不足，不能给出可靠结论；需要补充可验证的资料或样本记录。",
        "citations": [],
        "abstained": True,
        "confidence": 0.0,
    }


def offline_rag_answer(question: str, corpus: list[dict[str, Any]], top_k: int = 3) -> dict[str, Any]:
    evidence = retrieve_with_bm25(question, corpus, top_k=top_k)
    if _should_abstain(question, evidence):
        return _abstention_answer()

    citations = [row["chunk_id"] for row in evidence if row.get("score", 0) > 0]
    if not citations:
        return _abstention_answer()
    return {
        "answer": f"根据检索到的证据，相关信息见 {', '.join(f'[{cid}]' for cid in citations)}。",
        "citations": citations,
        "abstained": False,
        "confidence": min(1.0, max(row.get("score", 0.0) for row in evidence) / 5.0),
    }
