# Qwen3.5-Based MiniGeo Plan

## Model Selection

MiniGeo should use Qwen3.5-2B as the main model.

Model roles:

| Role | Model |
|---|---|
| Main model | Qwen3.5-2B |
| Lightweight baseline | Qwen3.5-0.8B |
| Strong baseline | Qwen3.5-4B |
| Teacher | Qwen3.5-27B or Qwen3.5-35B-A3B |
| Embedding | Qwen3-Embedding-0.6B |
| Reranker | Qwen3-Reranker-0.6B or bge-reranker |

## Why Qwen3.5-2B

Qwen3.5-2B is the best first main model because:

- It is more capable than 0.8B.
- It is easier to run than 4B or 9B.
- It is suitable for Colab Pro.
- It can support LoRA / QLoRA fine-tuning.
- It leaves room to show that RAG and verifier improve reliability beyond raw model scale.

## Development Order

1. Use Qwen3.5-2B without fine-tuning.
2. Build RAG.
3. Build MiniGeo-Bench.
4. Add verifier.
5. Run evaluation.
6. Fine-tune Qwen3.5-2B with LoRA / QLoRA.
7. Evaluate Qwen3.5-4B as a strong baseline.
8. Add Agent tools.

## LoRA / QLoRA Plan

First fine-tuning run:

| Setting | Value |
|---|---|
| Base model | Qwen3.5-2B |
| Method | QLoRA |
| Quantization | 4-bit |
| LoRA rank | 16 |
| Epochs | 1-3 |
| Data | Evidence-grounded QA, refusal, SQL-format examples |

Training objectives:

- Answer with citations.
- Refuse when evidence is insufficient.
- Follow output schemas.
- Generate SQL in controlled format.
- Avoid unsupported factual claims.

## Evaluation Hypotheses

The project should test these hypotheses:

1. Qwen3.5-2B + RAG outperforms Qwen3.5-2B on citation-grounded QA.
2. MiniGeo-SFT improves refusal and answer formatting.
3. Verifier reduces unsupported claim rate.
4. Qwen3.5-2B + RAG + Verifier can approach or exceed Qwen3.5-4B without RAG on reliability metrics.
5. Agent workflows improve database-backed questions over pure RAG.

## Main Result Table

| System | Acc | Citation Hit | Unsupported Claim | Abstention | SQL Exec | Latency |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5-0.8B | | | | | - | |
| Qwen3.5-2B | | | | | - | |
| Qwen3.5-2B + RAG | | | | | - | |
| MiniGeo-2B-SFT | | | | | - | |
| MiniGeo-2B-SFT + RAG | | | | | - | |
| MiniGeo-2B-SFT + RAG + Verifier | | | | | - | |
| Qwen3.5-4B + RAG | | | | | - | |
| MiniGeo-Agent | | | | | | |

## Resume Claim

Use this project claim after the system is implemented and evaluated:

> Built MiniGeo, a Qwen3.5-based geoscience trustworthy QA and data analysis agent system. Constructed MiniGeo-Bench, implemented hybrid RAG and citation verification, fine-tuned Qwen3.5-2B with LoRA, and evaluated answer accuracy, citation hit rate, hallucination rate, abstention accuracy, and SQL execution accuracy.

