# MiniGeo-Bench

## Purpose

MiniGeo-Bench is the evaluation foundation of MiniGeo. It measures whether the system can answer geoscience questions with evidence, refuse unsupported questions, and execute database-backed analysis tasks.

## Current MVP

The current MVP is `data/benchmark/minigeo_bench.jsonl`.

- Items: 50
- Answerable items: 41
- Unanswerable items: 9
- SQL-backed items: 8
- Evidence-labeled items: 35

Run:

```powershell
$env:PYTHONPATH="src"
python scripts/evaluate_bench.py
```

## Dataset Format

Each item is one JSON Lines record:

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

## Question Types

| Type | Purpose |
|---|---|
| `concept` | Basic geoscience concepts |
| `mineral_property` | Mineral physical or chemical properties |
| `spectroscopy` | Raman, infrared, or spectral characteristics |
| `evidence` | Questions that require cited document evidence |
| `multi_hop` | Questions requiring multiple evidence chunks |
| `unanswerable` | Questions with insufficient evidence |
| `false_premise` | Questions containing incorrect assumptions |
| `sql` | Questions requiring structured database queries |

## Annotation Rules

- Use concise reference answers.
- Use real `chunk_id` values for evidence-labeled questions.
- Set `answerable=false` when the correct behavior is refusal.
- For SQL questions, include `expected_sql_intent` and an `expected_result` object.
- Do not use MiniGeo-Bench reference answers as SFT output.

## Metrics

| Metric | Definition |
|---|---|
| `accuracy` | Whether the final answer matches the reference answer |
| `citation_hit_rate` | Whether cited chunks overlap gold evidence chunks |
| `unsupported_claim_rate` | Fraction of extracted claims not supported by evidence |
| `abstention_accuracy` | Whether unanswerable items trigger refusal |
| `sql_exec_accuracy` | Whether SQL executes and returns the expected result |
| `latency` | End-to-end response time |

