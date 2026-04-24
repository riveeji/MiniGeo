# MiniGeo Data Card

## Purpose

This document records data sources, processing rules, and known risks for MiniGeo. It should be updated whenever raw documents, benchmark items, RAG chunks, or SFT examples are added.

## Current Data Assets

| File | Purpose |
|---|---|
| `data/benchmark/minigeo_bench.jsonl` | 150-item MiniGeo-Bench seed benchmark |
| `data/processed/rag_corpus.jsonl` | 42 curated evidence chunks for local RAG tests |
| `data/processed/source_manifest.jsonl` | Source URL and license notes for curated seed expansion |
| `data/processed/minigeo_demo.sqlite` | Generated demo database, created by `scripts/init_demo_db.py` |

The current corpus is a curated seed corpus for pipeline validation. It includes source URLs and license notes, but it is still not enough for final research claims. Before reporting model results, expand it with more documented public sources and manually review source alignment.

## RAG Corpus Schema

```json
{
  "chunk_id": "doc_quartz#chunk_001",
  "doc_id": "doc_quartz",
  "text": "石英是常见的硅酸盐矿物，主要化学成分是二氧化硅 SiO2。",
  "source": "MiniGeo curated mineral notes",
  "url": "https://example.org/minigeo/quartz",
  "page": null,
  "topic": "concept",
  "mineral": "quartz",
  "license": "public"
}
```

## SFT Corpus Schema

```json
{
  "id": "sft_001",
  "instruction": "根据证据回答问题；如果证据不足，应明确拒答。",
  "input": "Question and evidence.",
  "output": "Grounded answer with citations.",
  "task_type": "evidence_qa"
}
```

## Processing Pipeline

```text
public source metadata
-> parse or manually curate
-> clean UTF-8 text
-> remove empty and duplicate chunks
-> assign stable chunk ids
-> add source, url, topic, mineral, license
-> export JSONL
-> run corpus validation and retrieval evaluation
```

## Data Quality Checks

- All text files must be UTF-8.
- Remove exact duplicate chunks.
- Remove empty or very short chunks.
- Track source URL and license where available.
- Keep benchmark reference answers out of SFT outputs.
- Report corpus size and topic distribution after each update.

## Leakage Control

- Do not train directly on MiniGeo-Bench reference answers.
- Evidence chunks may be available for open-book RAG evaluation, but answer text should not be reused as training output.
- Keep closed-book generation, open-book RAG, and SFT evaluation clearly separated.

## Licensing Notes

- Commit public metadata and processing scripts.
- Do not commit raw files whose redistribution status is unclear.
- For every non-curated source, record source name, URL, license, and redistribution status.
