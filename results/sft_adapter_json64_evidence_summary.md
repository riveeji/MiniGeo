# MiniGeo json64 Evidence-conditioned Final Smoke10

## Reparsed Smoke Evaluation

- Adapter: `checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter`
- Records: `results/sft_adapter_json64_evidence_smoke10_reparsed.jsonl`
- Dry run: `False`

## Summary

- items=10
- non_empty_answer_rate=1.000
- citation_hit_rate=1.000
- abstention_accuracy=1.000
- request_errors=0
- latency_ms=0.000

## Interpretation

- 该 smoke test 只检查 128step adapter 能否加载并按 JSON contract 生成输出。
- 质量结论需要后续在更大 benchmark 子集上比较 base / SFT / RAG / Verifier。

## Reparse Notes

- 本报告由已有 raw_model_output 离线重解析生成，没有重新调用模型。
- thinking_raw_outputs=0
- postprocessed_raw_outputs=0
- malformed_raw_json=1


## Format Diagnostics

- official_thinking_raw_outputs=0
- official_malformed_raw_json=1
- postprocessed_raw_outputs=0
- original_tail_pollution_outputs=0
