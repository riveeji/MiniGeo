# MiniGeo JSON-only SFT json64 Smoke Summary

# MiniGeo SFT Adapter Smoke Evaluation

- Adapter: `checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter`
- Records: `results/sft_adapter_json64_smoke10.jsonl`
- Dry run: `False`

## Summary

- items=10
- non_empty_answer_rate=1.000
- citation_hit_rate=0.000
- abstention_accuracy=0.100
- request_errors=0
- latency_ms=6440.721

## Interpretation

- 该 smoke test 只检查 128step adapter 能否加载并按 JSON contract 生成输出。
- 质量结论需要后续在更大 benchmark 子集上比较 base / SFT / RAG / Verifier。


## Format Diagnostics

- thinking_raw_outputs=0
- multi_json_raw_outputs=0

## Decision

- 若 thinking_raw_outputs 明显低于旧 128step 的 7/10，且 citation/refusal 不退化，可继续扩大到 128 或 553 step。
- 若 thinking 仍高，继续修 chat template 或训练文本，不跑 1 epoch。