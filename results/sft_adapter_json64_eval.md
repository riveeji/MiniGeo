# MiniGeo JSON-only SFT json64 Evaluation

本文件记录对 `F:\download-edge\minigeo_json64_sft_smoke_outputs.zip` 的本地检查结果。

## 结论

json64 短训验证了一个正向结果：`</think>` 泄漏从旧 128step 的 7/10 降到 0/10，说明 JSON-only corpus 和 `enable_thinking=false` 方向有效。

但本轮不能继续扩大训练。主要原因是 citation/refusal 明显退化，且 raw JSON 仍有语法错误。

| System | citation_hit_rate | abstention_accuracy | thinking_raw_outputs | malformed_raw_json | empty_citations_raw |
|---|---:|---:|---:|---:|---:|
| Qwen3.5-2B base smoke10 | 0.000 | 0.900 | 1/10 | - | - |
| MiniGeo-2B-SFT 128step smoke10 reparsed | 0.444 | 1.000 | 7/10 | - | - |
| MiniGeo-2B-SFT json64 smoke10 reparsed | 0.000 | 0.100 | 0/10 | 8/10 | 9/10 |

## 主要观察

- `request_errors=0`，adapter 可以加载和推理。
- `thinking_raw_outputs=0`，格式方向比旧 128step 更好。
- `citation_hit_rate=0.000`，新 adapter 基本不输出 benchmark evidence citation。
- `abstention_accuracy=0.100`，不可答题和可答题的 abstained 行为都不稳定。
- 8 条 raw output 不是合法 JSON，常见模式是 `" "abstained"` 这样的坏键名。
- 9 条 raw output 的 `citations` 为空。

## 评测设计备注

当前 SFT smoke prompt 只给 question，没有把 gold evidence block 放入 prompt。对于 citation 行为，这相当于 closed-book citation 评测，和 SFT corpus 中的 evidence-conditioned 训练样本不完全一致。

因此下一步不应该直接扩大到 553step 或 1 epoch，而应先做两件事：

1. 修改 SFT adapter smoke，使 evidence-labeled 题目带上 gold evidence block，再评估 citation behavior。
2. 修正 JSON key 生成问题，重点避免 `" "abstained"`、空 citation 和长重复答案。

当前本地代码已完成第 1 项：`evaluate_sft_adapter.py` 和 `evaluate_base_model.py` 会默认从 `data/processed/rag_corpus.jsonl` 读取 gold evidence，并注入 `Evidence:` block。下一轮 A100 只需要上传 json64 zip 复评，不需要重新训练。

## Artifact

| Field | Value |
|---|---|
| Zip path | `F:\download-edge\minigeo_json64_sft_smoke_outputs.zip` |
| Adapter path | `checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter` |
| Smoke records | 10 |
| Report | `results/sft_adapter_json64_summary.md` |

## 下一步

用 `docs/a100-json64-evidence-eval-cells.md` 跑 evidence-conditioned json64 smoke，而不是继续长训。
