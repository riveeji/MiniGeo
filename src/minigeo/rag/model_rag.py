import json
import re
from typing import Any, Protocol

from minigeo.rag.pipeline import assemble_evidence_prompt, retrieve_with_bm25
from minigeo.rag.tokenizer import tokenize


class TextGenerator(Protocol):
    def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        ...


JSON_ONLY_SYSTEM = (
    "You are a JSON API for MiniGeo. /no_think\n"
    "Return only the final JSON object. Do not reveal chain-of-thought, analysis, markdown, or schema examples."
)


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


def _normalize_citation(value: Any) -> str:
    return str(value).strip().strip("[]").strip()


def parse_model_answer(raw: str, allowed_citations: set[str]) -> dict[str, Any]:
    data = _extract_json_object(raw)
    if data is None:
        if _contains_thinking(raw):
            return {
                "answer": "",
                "citations": [],
                "abstained": True,
                "confidence": 0.0,
                "format_error": True,
            }
        citations = _extract_bracket_citations(raw, allowed_citations)
        return {
            "answer": raw.strip(),
            "citations": citations,
            "abstained": "证据不足" in raw or not citations,
            "confidence": 0.0 if not citations else 0.5,
        }

    citations = [
        normalized for citation in data.get("citations", [])
        if (normalized := _normalize_citation(citation)) in allowed_citations
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


def _contains_thinking(text: str) -> bool:
    lowered = text.lower()
    return "thinking process" in lowered or "<think>" in lowered


def assemble_json_rag_prompt(question: str, evidence: list[dict[str, Any]]) -> str:
    base_prompt = assemble_evidence_prompt(question, evidence)
    return (
        f"{base_prompt}\n\n"
        "Output only one JSON object. Do not output markdown, schema examples, or thinking process.\n"
        "If the model supports thinking modes, disable them for this answer.\n"
        "The JSON keys must be answer, citations, abstained, confidence.\n"
        "The answer value must be the final Chinese answer, never the literal word string.\n"
        "Use only retrieved chunk ids in citations. Every citation must directly support the answer text.\n"
        "必须引用直接支撑答案事实的 chunk id；不要引用泛化的系统说明来替代矿物、光谱或样本证据。\n"
        "If evidence is insufficient, set abstained to true."
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
    raw = client.generate(prompt, system=JSON_ONLY_SYSTEM, temperature=0.0, max_tokens=512)
    allowed = {row["chunk_id"] for row in positive_evidence}
    parsed = parse_model_answer(raw, allowed)
    parsed["citations"] = _repair_generic_citations(question, parsed, positive_evidence)
    parsed["evidence"] = positive_evidence
    parsed["raw_model_output"] = raw
    return parsed


def _repair_generic_citations(
    question: str,
    parsed: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> list[str]:
    citations = list(parsed.get("citations", []))
    if parsed.get("abstained") or not citations or _is_system_question(question):
        return citations
    evidence_by_id = {row["chunk_id"]: row for row in evidence}
    cited_chunks = [evidence_by_id[citation] for citation in citations if citation in evidence_by_id]
    if not cited_chunks:
        return citations
    domain_citations = [
        citation
        for citation in citations
        if citation in evidence_by_id and not _is_generic_system_chunk(evidence_by_id[citation])
    ]
    if domain_citations:
        return domain_citations

    candidates = [row for row in evidence if not _is_generic_system_chunk(row)]
    if not candidates:
        return citations
    best = max(candidates, key=lambda row: _direct_support_score(question, str(parsed.get("answer", "")), row))
    if _direct_support_score(question, str(parsed.get("answer", "")), best) <= 0:
        return citations
    return [best["chunk_id"]]


def _is_generic_system_chunk(chunk: dict[str, Any]) -> bool:
    return str(chunk.get("topic", "")) == "system" or str(chunk.get("doc_id", "")).startswith("doc_system")


def _is_system_question(question: str) -> bool:
    lowered = question.lower()
    keywords = [
        "rag",
        "verifier",
        "benchmark",
        "qlora",
        "sft",
        "agent",
        "sql",
        "citation",
        "引用格式",
        "系统",
        "泄漏",
        "延迟",
    ]
    return any(keyword in lowered for keyword in keywords)


def _direct_support_score(question: str, answer: str, chunk: dict[str, Any]) -> float:
    answer_tokens = set(tokenize(answer))
    question_tokens = set(tokenize(question))
    chunk_tokens = set(tokenize(str(chunk.get("text", ""))))
    if not chunk_tokens:
        return 0.0
    answer_overlap = len(answer_tokens & chunk_tokens) / max(1, len(answer_tokens))
    question_overlap = len(question_tokens & chunk_tokens) / max(1, len(question_tokens))
    return answer_overlap + 0.25 * question_overlap
