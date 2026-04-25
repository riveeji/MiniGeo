import json
import re
from typing import Any, Protocol

from minigeo.rag.pipeline import assemble_evidence_prompt, retrieve_with_bm25


class TextGenerator(Protocol):
    def generate(self, prompt: str) -> str:
        ...


def _extract_json_object(raw: str) -> dict[str, Any] | None:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    candidates: list[dict[str, Any]] = []
    for block in re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            candidates.append(data)
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", text):
        try:
            data, _ = decoder.raw_decode(text[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            candidates.append(data)
    for candidate in reversed(candidates):
        if _looks_like_answer_object(candidate):
            return candidate
    return None


def _looks_like_answer_object(data: dict[str, Any]) -> bool:
    answer = str(data.get("answer", "")).strip().lower()
    if not {"answer", "citations", "abstained", "confidence"}.issubset(data):
        return False
    if answer in {"", "string"}:
        return False
    return isinstance(data.get("citations"), list)


def _extract_bracket_citations(raw: str, allowed_citations: set[str]) -> list[str]:
    found = re.findall(r"\[([^\]]+)\]", raw)
    return [item for item in found if item in allowed_citations]


def parse_model_answer(raw: str, allowed_citations: set[str]) -> dict[str, Any]:
    data = _extract_json_object(raw)
    if data is None:
        citations = _extract_bracket_citations(raw, allowed_citations)
        return {
            "answer": raw.strip(),
            "citations": citations,
            "abstained": "证据不足" in raw or not citations,
            "confidence": 0.0 if not citations else 0.5,
        }

    citations = [
        citation for citation in data.get("citations", [])
        if citation in allowed_citations
    ]
    answer = str(data.get("answer", "")).strip()
    abstained = bool(data.get("abstained", False))
    if not citations and ("证据不足" in answer or "insufficient" in answer.lower()):
        abstained = True
    confidence = float(data.get("confidence", 0.0))
    return {
        "answer": answer,
        "citations": citations,
        "abstained": abstained,
        "confidence": max(0.0, min(1.0, confidence)),
    }


def assemble_json_rag_prompt(question: str, evidence: list[dict[str, Any]]) -> str:
    base_prompt = assemble_evidence_prompt(question, evidence)
    return (
        f"{base_prompt}\n\n"
        "Output only one JSON object. Do not output markdown, schema examples, or thinking process.\n"
        "The JSON keys must be answer, citations, abstained, confidence.\n"
        "The answer value must be the final Chinese answer, never the literal word string.\n"
        "Use only retrieved chunk ids in citations. If evidence is insufficient, set abstained to true."
    )


def generate_model_rag_answer(
    question: str,
    corpus: list[dict[str, Any]],
    client: TextGenerator,
    top_k: int = 5,
) -> dict[str, Any]:
    evidence = retrieve_with_bm25(question, corpus, top_k=top_k)
    positive_evidence = [row for row in evidence if row.get("score", 0.0) > 0]
    if not positive_evidence:
        return {
            "answer": "当前证据不足，不能给出可靠结论。",
            "citations": [],
            "abstained": True,
            "confidence": 0.0,
            "evidence": [],
            "raw_model_output": "",
        }
    prompt = assemble_json_rag_prompt(question, positive_evidence)
    raw = client.generate(prompt)
    allowed = {row["chunk_id"] for row in positive_evidence}
    parsed = parse_model_answer(raw, allowed)
    parsed["evidence"] = positive_evidence
    parsed["raw_model_output"] = raw
    return parsed
