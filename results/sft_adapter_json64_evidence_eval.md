# MiniGeo json64 Evidence-conditioned SFT 复评

本文记录对 `F:\download-edge\minigeo_json64_evidence_eval_outputs.zip` 的本地接入结果。

## 结论

json64 adapter 在注入 gold evidence block 后，citation 行为明显恢复：`citation_hit_rate=1.000`。本地 parser 加入“文字拒答与 `abstained` 字段一致性”重解析后，`abstention_accuracy` 从 0.900 提升到 1.000。随后 raw-output sanitizer 把 `minigeo_007` 中第一个完整 JSON 之后追加的 `</think>` 和第二段 JSON 保存到 `raw_model_output_original`，正式 `raw_model_output` 保留为单个合法 JSON。

这说明上一轮闭卷 json64 smoke 的 citation 失败主要来自评测 prompt 没有提供 evidence，而不是 adapter 完全丧失引用能力。但该结果仍不直接支持长训：原始模型输出中仍出现 1 条尾部污染，说明下一轮训练前还应继续用短 smoke 验证格式稳定性。

| System | citation_hit_rate | abstention_accuracy | thinking_raw_outputs | malformed_raw_json | empty_citations_raw |
|---|---:|---:|---:|---:|---:|
| MiniGeo-2B-SFT json64 smoke10 closed-book | 0.000 | 0.100 | 0/10 | 8/10 | 9/10 |
| MiniGeo-2B-SFT json64 evidence smoke10 reparsed | 1.000 | 1.000 | 0/10 | 0/10 | 1/10 |

## 导入文件

- `results/sft_adapter_json64_evidence_dryrun.jsonl`
- `results/sft_adapter_json64_evidence_dryrun.md`
- `results/sft_adapter_json64_evidence_smoke10.jsonl`
- `results/sft_adapter_json64_evidence_smoke10.md`
- `results/sft_adapter_json64_evidence_smoke10_reparsed.jsonl`
- `results/sft_adapter_json64_evidence_smoke10_reparsed.md`
- `results/sft_adapter_json64_evidence_summary.md`

## 问题样本

- `minigeo_007`：原始 raw output 先输出了一个可解析 JSON，随后又追加了 `</think>` 和第二段重复 JSON；当前 sanitizer 已将正式 `raw_model_output` 截取为第一个完整 JSON，并把原始文本保存在 `raw_model_output_original`。
- `minigeo_009`：gold evidence 为空，模型回答“当前证据不足”，但 raw JSON 中 `abstained=false`；当前 parser 已将这类文字拒答规范化为 `abstained=true`。

## 下一步

为了减少 A100 次数，暂时不跑新的训练。下一步优先在本地完成：

1. 暂不继续长训；下一次 A100 只用于短 smoke，验证新的 prompt / SFT 数据模板是否减少原始尾部污染。
2. 继续保留 `raw_model_output_original`，把模型真实格式问题和系统正式解析输出分开统计。
