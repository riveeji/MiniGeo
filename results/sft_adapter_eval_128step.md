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

2026-05-06 已补跑同题 base `Qwen/Qwen3.5-2B` smoke10 对照，结果见 `results/base_vs_sft_128step_smoke10.md`。

| System | citation_hit_rate | abstention_accuracy | thinking_raw_outputs |
|---|---:|---:|---:|
| Qwen3.5-2B base smoke10 | 0.000 | 0.900 | 1/10 |
| MiniGeo-2B-SFT 128step smoke10 reparsed | 0.444 | 1.000 | 7/10 |

结论：

1. 128step SFT 相比 base 改善了 citation/refusal 指标，说明训练信号有效。
2. SFT raw output 的 thinking 泄漏和多 JSON 问题仍然严重，不能直接进入长训。
3. 下一步先修 SFT 输出模板、训练样本格式和 generation prompt，再做下一轮短训或 smoke。
