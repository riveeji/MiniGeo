# MiniGeo SFT Adapter Smoke Evaluation

- Adapter: `checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter`
- Records: `results/sft_adapter_128step_dryrun.jsonl`
- Dry run: `True`

## Summary

- items=5
- non_empty_answer_rate=0.000
- citation_hit_rate=0.000
- abstention_accuracy=0.000
- request_errors=0
- latency_ms=0.000

## Interpretation

- 该 smoke test 只检查 128step adapter 能否加载并按 JSON contract 生成输出。
- 质量结论需要后续在更大 benchmark 子集上比较 base / SFT / RAG / Verifier。
