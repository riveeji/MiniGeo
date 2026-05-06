# MiniGeo Base Model Smoke Evaluation

- Base model: `Qwen/Qwen3.5-2B`
- Records: `results/base_qwen35_2b_smoke10.jsonl`
- Dry run: `False`

## Summary

- items=10
- non_empty_answer_rate=1.000
- citation_hit_rate=0.000
- abstention_accuracy=0.900
- request_errors=0
- latency_ms=7899.095

## Interpretation

- 该 smoke test 用作 128step SFT adapter 的同题 base model 对照。
- 质量结论需要与 SFT adapter、RAG 和 Verifier 在同一题集上比较。
