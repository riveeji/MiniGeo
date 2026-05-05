from __future__ import annotations

import json
from pathlib import Path
import re
from time import perf_counter
from typing import Any

from minigeo.benchmark import load_benchmark
from minigeo.eval.model_service import summarize_model_rag_outputs
from minigeo.jsonl import write_jsonl
from minigeo.rag.model_rag import parse_model_answer


SFT_JSON_SYSTEM = (
    "你是 MiniGeo。请用中文回答地学问题。"
    "只输出最终 JSON，不输出思考过程、Markdown 或解释性前缀。"
)


def validate_adapter_dir(adapter_dir: Path) -> list[str]:
    errors = []
    if not adapter_dir.exists():
        return [f"missing adapter directory: {adapter_dir}"]
    if not (adapter_dir / "adapter_config.json").exists():
        errors.append("missing adapter_config.json")
    if not (adapter_dir / "adapter_model.safetensors").exists():
        errors.append("missing adapter_model.safetensors")
    return errors


def build_sft_prompt(question: str) -> str:
    return (
        "System: 你是 MiniGeo，回答必须简短、可信，并遵守输出格式。\n"
        f"User: {question}\n\n"
        "Output only one JSON object. Do not output markdown, schema examples, or thinking process.\n"
        "The JSON keys must be answer, citations, abstained, confidence.\n"
        "If evidence is not provided, citations should be an empty list.\n"
        "如果不能可靠回答，请将 abstained 设为 true。"
    )


def parse_adapter_answer(raw: str, allowed_citations: set[str]) -> dict[str, Any]:
    merged = _merge_json_fragments(raw, allowed_citations)
    fallback = parse_model_answer(raw, allowed_citations)
    if not merged:
        return fallback
    return {
        "answer": merged.get("answer") or fallback.get("answer", ""),
        "citations": merged.get("citations") or fallback.get("citations", []),
        "abstained": bool(merged.get("abstained", fallback.get("abstained", False))),
        "confidence": float(merged.get("confidence", fallback.get("confidence", 0.0))),
    }


def _merge_json_fragments(raw: str, allowed_citations: set[str]) -> dict[str, Any]:
    fragments = _extract_json_fragments(raw)
    answer = ""
    citations: list[str] = []
    abstained: bool | None = None
    confidence: float | None = None
    for fragment in fragments:
        if isinstance(fragment.get("answer"), str) and fragment["answer"].strip():
            answer = fragment["answer"].strip()
        citations.extend(_normalise_adapter_citations(fragment.get("citations"), allowed_citations))
        citations.extend(_normalise_adapter_citations(fragment.get("source"), allowed_citations))
        if "abstained" in fragment:
            abstained = bool(fragment["abstained"])
        if "confidence" in fragment:
            try:
                confidence = max(0.0, min(1.0, float(fragment["confidence"])))
            except (TypeError, ValueError):
                pass
    citations.extend(_extract_allowed_citations_from_text(raw, allowed_citations))
    unique_citations = []
    for citation in citations:
        if citation not in unique_citations:
            unique_citations.append(citation)
    if not answer and not unique_citations and abstained is None and confidence is None:
        return {}
    return {
        "answer": answer,
        "citations": unique_citations,
        "abstained": abstained if abstained is not None else False,
        "confidence": confidence if confidence is not None else (0.0 if abstained else 0.5),
    }


def _extract_json_fragments(raw: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    fragments = []
    for match in re.finditer(r"\{", raw):
        try:
            data, _ = decoder.raw_decode(raw[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            fragments.append(data)
    return fragments


def _normalise_adapter_citations(value: Any, allowed_citations: set[str]) -> list[str]:
    if value is None:
        return []
    if isinstance(value, dict):
        values = [value.get("id") or value.get("chunk_id") or value.get("source")]
    elif isinstance(value, list):
        values = []
        for item in value:
            if isinstance(item, dict):
                values.append(item.get("id") or item.get("chunk_id") or item.get("source"))
            else:
                values.append(item)
    else:
        values = [value]
    return [
        citation for item in values
        if (citation := _map_adapter_citation(str(item).strip().strip("[]").strip("\"'"), allowed_citations))
    ]


def _extract_allowed_citations_from_text(raw: str, allowed_citations: set[str]) -> list[str]:
    citations = []
    tokens = set(re.findall(r"[A-Za-z0-9_]+#chunk_\d+", raw))
    tokens.update(re.findall(r"[A-Za-z]+#chunk_\d+", raw))
    for token in tokens:
        mapped = _map_adapter_citation(token, allowed_citations)
        if mapped:
            citations.append(mapped)
    return citations


def _map_adapter_citation(candidate: str, allowed_citations: set[str]) -> str | None:
    if candidate in allowed_citations:
        return candidate
    if candidate and f"doc_{candidate}" in allowed_citations:
        return f"doc_{candidate}"
    for allowed in allowed_citations:
        if candidate and allowed.endswith(candidate):
            return allowed
    return None


def select_adapter_smoke_rows(benchmark_path: Path, limit: int) -> list[dict[str, Any]]:
    rows = load_benchmark(benchmark_path)
    preferred = [
        row for row in rows
        if row.get("type") in {"concept", "mineral_property", "spectroscopy", "unanswerable", "false_premise"}
    ]
    return (preferred or rows)[:limit]


def dry_run_records(rows: list[dict[str, Any]], adapter_dir: Path) -> list[dict[str, Any]]:
    return [
        {
            "id": row["id"],
            "question": row["question"],
            "gold_evidence": row.get("evidence", []),
            "adapter_dir": str(adapter_dir),
            "prompt": build_sft_prompt(row["question"]),
            "result": {
                "answer": "",
                "citations": [],
                "abstained": True,
                "confidence": 0.0,
                "raw_model_output": "",
                "dry_run": True,
            },
        }
        for row in rows
    ]


def reparse_adapter_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reparsed_records = []
    for record in records:
        output = dict(record.get("result", {}))
        raw = str(output.get("raw_model_output", ""))
        reparsed = parse_adapter_answer(raw, allowed_citations=set(record.get("gold_evidence", [])))
        reparsed["raw_model_output"] = raw
        if output.get("error"):
            reparsed["error"] = output["error"]
        updated = dict(record)
        updated["result"] = reparsed
        updated["reparsed"] = True
        reparsed_records.append(updated)
    return reparsed_records


def run_adapter_smoke(
    adapter_dir: Path,
    base_model: str,
    benchmark_path: Path,
    output_path: Path,
    limit: int,
    max_new_tokens: int,
    dry_run: bool = False,
) -> dict[str, Any]:
    errors = validate_adapter_dir(adapter_dir)
    rows = select_adapter_smoke_rows(benchmark_path, limit=limit)
    if dry_run:
        records = dry_run_records(rows, adapter_dir)
        write_jsonl(output_path, records)
        summary = summarize_model_rag_outputs(rows, {row["id"]: record["result"] for row, record in zip(rows, records)})
        summary["adapter_errors"] = errors
        summary["dry_run"] = True
        return summary
    if errors:
        raise FileNotFoundError("; ".join(errors))

    generator = _PeftAdapterGenerator(adapter_dir=adapter_dir, base_model=base_model, max_new_tokens=max_new_tokens)
    records = []
    outputs = {}
    started = perf_counter()
    for row in rows:
        prompt = build_sft_prompt(row["question"])
        raw = generator.generate(prompt)
        parsed = parse_adapter_answer(raw, allowed_citations=set(row.get("evidence", [])))
        parsed["raw_model_output"] = raw
        outputs[row["id"]] = parsed
        records.append(
            {
                "id": row["id"],
                "question": row["question"],
                "gold_evidence": row.get("evidence", []),
                "adapter_dir": str(adapter_dir),
                "prompt": prompt,
                "result": parsed,
            }
        )
        write_jsonl(output_path, records)
    latency_ms = (perf_counter() - started) * 1000.0 / max(len(rows), 1)
    summary = summarize_model_rag_outputs(rows, outputs, latency_ms=latency_ms)
    summary["adapter_errors"] = []
    summary["dry_run"] = False
    return summary


class _PeftAdapterGenerator:
    def __init__(self, adapter_dir: Path, base_model: str, max_new_tokens: int):
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        self.tokenizer = AutoTokenizer.from_pretrained(adapter_dir, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        quantization = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        base = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=quantization,
            device_map="auto",
            trust_remote_code=True,
        )
        self.model = PeftModel.from_pretrained(base, adapter_dir)
        self.model.eval()
        self.max_new_tokens = max_new_tokens

    def generate(self, prompt: str) -> str:
        import torch

        messages = [
            {"role": "system", "content": SFT_JSON_SYSTEM},
            {"role": "user", "content": prompt},
        ]
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            generated = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        output_ids = generated[0][inputs["input_ids"].shape[-1]:]
        return self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()


def format_sft_adapter_report(
    adapter_dir: Path,
    summary: dict[str, Any],
    records_path: Path,
    dry_run: bool,
) -> str:
    lines = [
        "# MiniGeo SFT Adapter Smoke Evaluation",
        "",
        f"- Adapter: `{adapter_dir.as_posix()}`",
        f"- Records: `{records_path.as_posix()}`",
        f"- Dry run: `{dry_run}`",
        "",
        "## Summary",
        "",
        f"- items={summary.get('items', 0)}",
        f"- non_empty_answer_rate={summary.get('non_empty_answer_rate', 0.0):.3f}",
        f"- citation_hit_rate={summary.get('citation_hit_rate', 0.0):.3f}",
        f"- abstention_accuracy={summary.get('abstention_accuracy', 0.0):.3f}",
        f"- request_errors={summary.get('request_errors', 0)}",
        f"- latency_ms={summary.get('latency_ms', 0.0):.3f}",
        "",
    ]
    errors = summary.get("adapter_errors") or []
    if errors:
        lines.extend(["## Adapter Errors", "", *[f"- {error}" for error in errors], ""])
    lines.extend(
        [
            "## Interpretation",
            "",
            "- 该 smoke test 只检查 128step adapter 能否加载并按 JSON contract 生成输出。",
            "- 质量结论需要后续在更大 benchmark 子集上比较 base / SFT / RAG / Verifier。",
            "",
        ]
    )
    return "\n".join(lines)
