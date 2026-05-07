# MiniGeo SFT Adapter Smoke Evaluation

- Adapter: `checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter`
- Records: `results/sft_adapter_json64_evidence_smoke10.jsonl`
- Dry run: `False`

## Summary

- items=10
- non_empty_answer_rate=1.000
- citation_hit_rate=1.000
- abstention_accuracy=1.000
- request_errors=0
- latency_ms=10569.676

## Interpretation

- 该 smoke test 只检查 128step adapter 能否加载并按 JSON contract 生成输出。
- 质量结论需要后续在更大 benchmark 子集上比较 base / SFT / RAG / Verifier。
