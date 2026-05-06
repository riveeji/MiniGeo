# Base 2B vs SFT 128step Smoke10 对照

## Base 2B

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


## SFT 128step Reparsed

# MiniGeo SFT Adapter Smoke Evaluation

- Adapter: `checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter`
- Records: `results/sft_adapter_128step_smoke10_reparsed.jsonl`
- Dry run: `False`

## Summary

- items=10
- non_empty_answer_rate=1.000
- citation_hit_rate=0.444
- abstention_accuracy=1.000
- request_errors=0
- latency_ms=0.000

## Interpretation

- 该 smoke test 只检查 128step adapter 能否加载并按 JSON contract 生成输出。
- 质量结论需要后续在更大 benchmark 子集上比较 base / SFT / RAG / Verifier。

## Reparse Notes

- 本报告由已有 raw_model_output 离线重解析生成，没有重新调用模型。
- thinking_raw_outputs=7


## 判读规则

- 如果 SFT 的 citation_hit_rate、abstention_accuracy 或 JSON 格式明显优于 base，再考虑 553step 或 1 epoch。
- 如果 SFT 仍大量输出 `</think>` 或多 JSON，先修训练样本格式和 prompt，不继续长训。
