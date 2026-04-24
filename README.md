# MiniGeo

MiniGeo is a Qwen3.5-based geoscience trustworthy QA and data analysis agent project. The contribution is not a new foundation model; it is a measurable domain system that combines MiniGeo-Bench, retrieval-augmented generation, evidence verification, QLoRA-ready adaptation, and SQL-backed agent workflows.

## Current Status

Implemented locally:

- Python package skeleton under `src/minigeo`.
- 150-item UTF-8 MiniGeo-Bench seed benchmark.
- 42-chunk curated seed RAG corpus with stable `chunk_id` values.
- Chinese-aware tokenizer with optional `jieba` and fallback character bigrams.
- Pure-Python BM25 retriever.
- Retrieval metrics: `recall@k`, `MRR`, `citation_hit_rate`.
- Simple verifier contract and heuristic verifier.
- SQLite demo database and SQL execution tool.
- Minimal Agent report interface.
- QLoRA config placeholder for Colab Pro training.

Not implemented locally:

- Real Qwen3.5 model inference.
- Dense retrieval and reranker inference.
- QLoRA training.
- Full model-backed evaluation table.

Those stages require Colab Pro or a running model service.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:PYTHONPATH="src"
pytest -q
```

If you only want to run the standard-library parts, `pytest` works without installing the heavy model dependencies.

## Useful Commands

```powershell
$env:PYTHONPATH="src"
python scripts/evaluate_bench.py
python scripts/expand_seed_data.py
python scripts/prepare_data.py
python scripts/evaluate_retrieval.py
python scripts/rag_demo.py
python scripts/evaluate_verifier.py
python scripts/sql_demo.py
python scripts/agent_demo.py
```

## Core Interfaces

Benchmark item:

```json
{
  "id": "minigeo_001",
  "question": "石英的主要化学成分是什么？",
  "answer": "石英的主要化学成分是二氧化硅。",
  "type": "concept",
  "difficulty": "easy",
  "answerable": true,
  "requires_sql": false,
  "evidence": ["doc_quartz#chunk_001"],
  "expected_sql_intent": null,
  "expected_result": null
}
```

RAG answer:

```json
{
  "answer": "...",
  "citations": ["doc_quartz#chunk_001"],
  "abstained": false,
  "confidence": 0.7
}
```

Verifier report:

```json
{
  "verdict": "supported",
  "claims": [
    {
      "claim": "...",
      "status": "supported",
      "evidence": ["doc_quartz#chunk_001"],
      "confidence": 0.8
    }
  ]
}
```

## Roadmap

1. Expand MiniGeo-Bench from 150 to 300+ items.
2. Replace or strengthen the curated seed corpus with more documented public geoscience sources.
3. Add Qwen3.5-2B model-backed RAG through an OpenAI-compatible endpoint.
4. Add Qwen3-Embedding-0.6B dense retrieval and Qwen3-Reranker-0.6B reranking.
5. Improve verifier with model-backed claim extraction and support classification.
6. Run QLoRA SFT in Colab Pro using `configs/qwen35_2b_lora.yaml`.
7. Expand SQL evaluation and MiniGeo-Agent.
8. Fill `results/main_results.md` and `results/failure_cases.md`.

## Project Claim

MiniGeo studies whether a lightweight Qwen3.5-based system can improve geoscience QA reliability through domain RAG, citation verification, and agentic data analysis, rather than relying only on model scale.
