from typing import Any, Protocol

from minigeo.rag.model_rag import TextGenerator, generate_model_rag_answer
from minigeo.verifier.verifier import MiniGeoVerifier


class Verifier(Protocol):
    def verify(self, answer: str, evidence_chunks: list[dict[str, Any]]) -> dict[str, Any]:
        ...


ACCEPTED_VERDICTS = {"supported"}


def verify_rag_answer(answer: dict[str, Any], verifier: Verifier | None = None) -> dict[str, Any]:
    verified = dict(answer)
    if verified.get("abstained"):
        verified["verification"] = {"verdict": "skipped", "claims": []}
        verified["verifier_action"] = "skipped_abstained"
        return verified

    evidence = list(verified.get("evidence") or [])
    report = (verifier or MiniGeoVerifier()).verify(str(verified.get("answer", "")), evidence)
    verified["verification"] = report
    if report.get("verdict") in ACCEPTED_VERDICTS:
        verified["verifier_action"] = "accepted"
        return verified

    verified["unverified_answer"] = str(verified.get("answer", ""))
    verified["answer"] = "当前证据不足，不能确认原始回答中的全部事实，因此拒绝给出可靠结论。"
    verified["citations"] = []
    verified["abstained"] = True
    verified["confidence"] = 0.0
    verified["verifier_action"] = "abstained"
    return verified


def generate_verified_model_rag_answer(
    question: str,
    corpus: list[dict[str, Any]],
    client: TextGenerator,
    verifier: Verifier | None = None,
    top_k: int = 5,
) -> dict[str, Any]:
    answer = generate_model_rag_answer(question, corpus, client, top_k=top_k)
    return verify_rag_answer(answer, verifier=verifier)
