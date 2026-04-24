# MiniGeo Architecture

## System Overview

MiniGeo is organized as a layered system:

```text
User Question
  |
  v
Task Router / Agent Planner
  |
  +--> Document RAG
  |      +--> Chunk index
  |      +--> BM25 retriever
  |      +--> Embedding retriever
  |      +--> Reranker
  |
  +--> SQL Tooling
  |      +--> Schema reader
  |      +--> SQL generator
  |      +--> SQL executor
  |      +--> SQL repair
  |
  +--> Qwen3.5 Generator
  |
  +--> Citation Verifier
         +--> Claim extraction
         +--> Evidence matching
         +--> Support classification
         +--> Rewrite or abstain
```

## Layer 1: Model Layer

Main model:

- Qwen3.5-2B.

Baselines:

- Qwen3.5-0.8B.
- Qwen3.5-4B.

Teacher models:

- Qwen3.5-27B.
- Qwen3.5-35B-A3B.

Model responsibilities:

- Understand user questions.
- Generate answers from evidence.
- Generate SQL when needed.
- Produce short reasoning summaries.
- Support tool-use format in the agent layer.

## Layer 2: RAG Layer

RAG provides external geoscience knowledge.

Main components:

- Document parser.
- Chunker.
- Metadata store.
- BM25 retriever.
- Embedding retriever.
- Reranker.
- Prompt assembler.

Chunk schema:

```json
{
  "chunk_id": "doc_001#chunk_003",
  "doc_id": "doc_001",
  "text": "The chunk content.",
  "source": "mineral_spectroscopy.pdf",
  "page": 12,
  "topic": "spectroscopy",
  "mineral": "quartz"
}
```

## Layer 3: Verifier Layer

The verifier checks whether the answer is supported by retrieved evidence.

Input:

- User question.
- Generated answer.
- Retrieved evidence chunks.

Output:

```json
{
  "verdict": "supported",
  "claims": [
    {
      "claim": "Quartz has a strong Raman peak near 464 cm-1.",
      "status": "supported",
      "evidence": ["doc_001#chunk_003"]
    }
  ]
}
```

Verdict labels:

- `supported`
- `partially_supported`
- `unsupported`
- `contradicted`
- `insufficient_evidence`

## Layer 4: Agent Layer

The agent decides which tools to call.

Supported tools:

| Tool | Input | Output |
|---|---|---|
| `search_docs` | question | evidence chunks |
| `generate_sql` | question and schema | SQL query |
| `execute_sql` | SQL query | table result |
| `repair_sql` | SQL and error message | repaired SQL |
| `verify_answer` | answer and evidence | verification report |
| `write_report` | verified results | final report |

Example workflow:

```text
Question: Which minerals are most often misclassified in Qinhuangdao samples and why?

1. Read database schema.
2. Generate SQL to find misclassification pairs.
3. Execute SQL.
4. Retrieve documents for the top confused mineral categories.
5. Generate explanation with citations.
6. Verify claims.
7. Return answer, SQL, evidence, and verification report.
```

## Evaluation Layer

MiniGeo must evaluate both language quality and system reliability.

Metrics:

- Answer accuracy.
- Citation hit rate.
- Unsupported claim rate.
- Hallucination rate.
- Abstention accuracy.
- SQL execution accuracy.
- SQL repair success rate.
- Latency.

