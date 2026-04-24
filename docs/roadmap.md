# MiniGeo Roadmap

## Goal

Build MiniGeo as a Qwen3.5-based geoscience trustworthy QA and data analysis system. The final system should combine RAG, evidence verification, LoRA fine-tuning, benchmark evaluation, and an agent layer for SQL-backed analysis.

## Guiding Principle

The project should not compete on model size. It should compete on:

- Domain benchmark quality.
- Evidence-grounded generation.
- Refusal behavior when evidence is insufficient.
- Structured and unstructured data integration.
- Clear evaluation and ablation results.

## Phase 0: Project Setup

Duration: 1 day.

Deliverables:

- Git repository.
- Python environment.
- Basic directories.
- README and docs.
- First Colab notebook template.

Recommended dependencies:

```text
torch
transformers
peft
bitsandbytes
datasets
accelerate
sentence-transformers
faiss-cpu
rank-bm25
pandas
numpy
scikit-learn
tqdm
pyyaml
fastapi
uvicorn
gradio
```

## Phase 1: MiniGeo-Bench

Duration: 3-5 days.

Purpose: Build the project evaluation foundation before implementing complicated modeling.

Target size:

- MVP: 50 questions.
- Resume-ready version: 150-300 questions.
- Strong version: 300+ questions with evidence labels.

Question types:

| Type | Description |
|---|---|
| concept | Basic geoscience concepts |
| mineral_property | Mineral physical and chemical properties |
| spectroscopy | Raman, infrared, or spectral characteristics |
| evidence | Questions requiring citation from documents |
| multi_hop | Questions requiring multiple evidence chunks |
| unanswerable | Questions with insufficient evidence |
| false_premise | Questions containing incorrect assumptions |
| sql | Questions requiring structured database queries |

Deliverables:

- `data/benchmark/minigeo_bench.jsonl`
- `docs/benchmark.md`
- `scripts/evaluate_bench.py`

## Phase 2: Data Pipeline

Duration: 4-7 days.

Purpose: Turn raw geoscience documents into RAG chunks and SFT training examples.

Pipeline:

```text
raw documents
-> parsing
-> cleaning
-> deduplication
-> chunking
-> metadata tagging
-> train / validation / test split
-> RAG corpus and SFT corpus
```

Deliverables:

- `scripts/prepare_data.py`
- `data/processed/rag_corpus.jsonl`
- `data/processed/sft_corpus.jsonl`
- `docs/data-card.md`

## Phase 3: Qwen3.5-2B RAG MVP

Duration: 5-7 days.

Purpose: Build the first usable MiniGeo system before fine-tuning.

Pipeline:

```text
question
-> BM25 retrieval
-> embedding retrieval
-> hybrid merge
-> rerank
-> evidence prompt construction
-> Qwen3.5-2B generation
-> cited answer
```

Deliverables:

- `src/minigeo/rag/chunker.py`
- `src/minigeo/rag/indexer.py`
- `src/minigeo/rag/retriever.py`
- `src/minigeo/rag/reranker.py`
- `src/minigeo/rag/pipeline.py`
- `scripts/build_index.py`
- `scripts/rag_demo.py`

Success criteria:

- The demo can answer at least 20 benchmark questions.
- Each answer includes source chunk ids.
- RAG improves citation hit rate over Qwen3.5-2B without retrieval.

## Phase 4: MiniGeo-Verifier

Duration: 5-7 days.

Purpose: Make MiniGeo different from ordinary RAG by checking evidence support.

Verifier workflow:

```text
answer
-> claim extraction
-> evidence matching
-> support classification
-> rewrite or abstain when unsupported
```

Labels:

- `supported`
- `contradicted`
- `insufficient`

Deliverables:

- `src/minigeo/verifier/claim_extractor.py`
- `src/minigeo/verifier/evidence_matcher.py`
- `src/minigeo/verifier/verifier.py`
- `scripts/evaluate_verifier.py`
- `results/verifier_eval.md`

Success criteria:

- Unsupported claim rate is measurable.
- Unanswerable questions trigger refusals.
- The verifier can explain which evidence supports or fails to support a claim.

## Phase 5: Qwen3.5-2B LoRA / QLoRA

Duration: 7-10 days.

Purpose: Create `MiniGeo-Qwen3.5-2B-SFT`.

Training data:

- Geoscience QA.
- Evidence-grounded answers.
- Refusal samples.
- SQL generation samples.
- Reasoning distillation samples.

Training strategy:

- Use QLoRA first.
- Compare LoRA rank 8, 16, and 32 if time allows.
- Keep the first run small and reproducible.

Deliverables:

- `configs/qwen35_2b_lora.yaml`
- `scripts/train_lora.py`
- `src/minigeo/finetune/`
- `results/sft_eval.md`

Success criteria:

- SFT improves domain answer style or refusal behavior.
- RAG + Verifier remains the strongest reliability configuration.

## Phase 6: Qwen3.5-4B Strong Baseline

Duration: 3-5 days.

Purpose: Show whether a smaller model with RAG and verification can approach or outperform a larger no-RAG baseline.

Evaluation groups:

- Qwen3.5-2B.
- Qwen3.5-2B + RAG.
- MiniGeo-Qwen3.5-2B-SFT + RAG.
- MiniGeo-Qwen3.5-2B-SFT + RAG + Verifier.
- Qwen3.5-4B.
- Qwen3.5-4B + RAG.

Deliverable:

- `results/main_results.md`

## Phase 7: MiniGeo-Agent

Duration: 7-14 days.

Purpose: Upgrade from trustworthy QA to data analysis.

Agent tools:

| Tool | Purpose |
|---|---|
| `search_docs` | Search geoscience documents |
| `retrieve_evidence` | Return evidence chunks |
| `generate_sql` | Generate SQL from natural language |
| `execute_sql` | Execute SQL against demo database |
| `repair_sql` | Repair failed SQL using error messages and schema |
| `verify_answer` | Check final answer support |
| `write_report` | Summarize evidence-backed analysis |

Deliverables:

- `src/minigeo/agent/`
- `scripts/init_demo_db.py`
- `scripts/agent_demo.py`
- `docs/agent-design.md`

Success criteria:

- The agent can answer mixed document and database questions.
- SQL execution accuracy is measurable.
- Failed SQL can be repaired in simple cases.
- Final answers include evidence and verification results.

## Phase 8: Optional MiniGeo-Tiny

Duration: 7-10 days.

Purpose: Demonstrate understanding of the LLM training chain.

This is not the main project contribution.

Features:

- Tokenizer training.
- Decoder-only Transformer.
- RoPE.
- RMSNorm.
- SwiGLU.
- KV cache.
- Pretraining.
- SFT.

Expected size:

- Tiny: 10M-30M parameters.
- Base: 50M-150M parameters.

## Phase 9: Packaging

Duration: 3-5 days.

Final artifacts:

- README.
- Architecture diagram.
- MiniGeo-Bench documentation.
- Data card.
- Main result table.
- Failure case analysis.
- Colab notebook.
- Resume bullet.

Final resume positioning:

> MiniGeo: Built a Qwen3.5-based geoscience trustworthy QA and data analysis agent system, including domain benchmark construction, hybrid RAG, citation verification, LoRA fine-tuning, and Text-to-SQL agent workflows.

