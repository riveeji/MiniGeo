from typing import Any

from minigeo.rag.bm25 import BM25Retriever


def assemble_evidence_prompt(question: str, evidence: list[dict[str, Any]]) -> str:
    chunks = "\n".join(
        f"[{row['chunk_id']}] {row['text']}" for row in evidence
    )
    return (
        "Answer the geoscience question using only the evidence below. "
        "If evidence is insufficient, refuse briefly and say evidence is insufficient. "
        "Cite chunk ids in brackets.\n\n"
        f"Question: {question}\n\nEvidence:\n{chunks}\n\nAnswer:"
    )


def retrieve_with_bm25(question: str, corpus: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
    return BM25Retriever(corpus).search(question, top_k=top_k)


def offline_rag_answer(question: str, corpus: list[dict[str, Any]], top_k: int = 3) -> dict[str, Any]:
    evidence = retrieve_with_bm25(question, corpus, top_k=top_k)
    citations = [row["chunk_id"] for row in evidence if row.get("score", 0) > 0]
    if not citations:
        return {
            "answer": "当前证据不足，不能给出可靠结论。",
            "citations": [],
            "abstained": True,
            "confidence": 0.0,
        }
    return {
        "answer": f"根据检索到的证据，相关信息见 {', '.join(f'[{cid}]' for cid in citations)}。",
        "citations": citations,
        "abstained": False,
        "confidence": min(1.0, max(row.get("score", 0.0) for row in evidence) / 5.0),
    }

