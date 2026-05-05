# MiniGeo SFT Adapter 128step Evaluation Artifact Audit

本文件记录对 `F:\download-edge\minigeo_sft_adapter_eval_128step (1).zip` 的本地检查结果。

## 结论

128step SFT adapter 已完成真实推理 smoke10。当前结果说明 adapter 能加载并生成非空回答，但格式和引用行为仍不稳定，不能作为最终 SFT 质量提升结论。

压缩包中包含：

- `results/sft_adapter_128step_dryrun.jsonl`
- `results/sft_adapter_128step_dryrun.md`
- `results/sft_adapter_128step_smoke10.jsonl`
- `results/sft_adapter_128step_smoke10.md`

原始 smoke10 指标：

| Metric | Value |
|---|---:|
| items | 10 |
| non_empty_answer_rate | 1.000 |
| citation_hit_rate | 0.111 |
| abstention_accuracy | 0.400 |
| request_errors | 0 |
| latency_ms | 14435.206 |
| raw outputs containing `</think>` | 7 |

离线重解析后指标：

| Metric | Value |
|---|---:|
| items | 10 |
| non_empty_answer_rate | 1.000 |
| citation_hit_rate | 0.444 |
| abstention_accuracy | 1.000 |
| request_errors | 0 |
| thinking_raw_outputs | 7 |

## 主要观察

- adapter 加载和生成链路已跑通，`request_errors=0`。
- 10 条输出均非空，说明 128step adapter 能完成推理。
- `citation_hit_rate=0.111`，多数 citation 不是 benchmark 中的 `doc_id#chunk_id` 格式，或引用未被 parser 识别。
- `abstention_accuracy=0.400`，拒答行为仍不稳。
- 7 条 raw output 包含 `</think>`，并且多条输出是多个 JSON 对象串联，不满足“只输出一个 JSON 对象”的目标。
- 本地 parser 改进后，离线重解析把 `citation_hit_rate` 提升到 0.444，并把 `abstention_accuracy` 修正到 1.000；这说明部分问题是解析失败，不全是模型内容错误。
- `thinking_raw_outputs=7` 没有因离线重解析消失，说明下一次 A100 生成仍需要改 prompt、chat template 或训练样本格式。

## Artifact

| Field | Value |
|---|---|
| Zip path | `F:\download-edge\minigeo_sft_adapter_eval_128step (1).zip` |
| Zip SHA256 | `9ED39BAB57FEA226E20DA870BD4ACA0F6864EED6A0E8252B617B72AFB81B5290` |
| Zip size | 4103 bytes |
| Dry-run records | 5 |
| Smoke10 records | 10 |
| Smoke10 report found | Yes |

## 下一步

1. 先把 128step 结果作为中性 smoke 结果保留：训练链路有效，离线解析可改善指标，但原始生成格式约束不足。
2. 在同一 10 题子集上补 base `Qwen/Qwen3.5-2B` 对照，判断 128step adapter 是否真的改善 answer format、refusal 或 citation behavior。
3. 下一次 A100 生成前继续收紧 prompt/chat template，重点减少 `</think>` 和多 JSON 串联。
