# MiniGeo json64 Evidence-conditioned SFT 复评

本文记录对 `F:\download-edge\minigeo_json64_evidence_eval_outputs.zip` 的本地接入结果。

## 结论

json64 adapter 在注入 gold evidence block 后，citation 行为明显恢复：`citation_hit_rate=1.000`，`abstention_accuracy=0.900`。这说明上一轮闭卷 json64 smoke 的 citation 失败主要来自评测 prompt 没有提供 evidence，而不是 adapter 完全丧失引用能力。

但该结果还不能直接支持继续长训。当前 10 题 smoke 中仍有 `thinking_raw_outputs=1/10`、`malformed_raw_json=1/10`、`empty_citations_raw=1/10`，说明 JSON 输出约束仍需继续加固。

| System | citation_hit_rate | abstention_accuracy | thinking_raw_outputs | malformed_raw_json | empty_citations_raw |
|---|---:|---:|---:|---:|---:|
| MiniGeo-2B-SFT json64 smoke10 closed-book | 0.000 | 0.100 | 0/10 | 8/10 | 9/10 |
| MiniGeo-2B-SFT json64 evidence smoke10 reparsed | 1.000 | 0.900 | 1/10 | 1/10 | 1/10 |

## 导入文件

- `results/sft_adapter_json64_evidence_dryrun.jsonl`
- `results/sft_adapter_json64_evidence_dryrun.md`
- `results/sft_adapter_json64_evidence_smoke10.jsonl`
- `results/sft_adapter_json64_evidence_smoke10.md`
- `results/sft_adapter_json64_evidence_smoke10_reparsed.jsonl`
- `results/sft_adapter_json64_evidence_smoke10_reparsed.md`
- `results/sft_adapter_json64_evidence_summary.md`

## 问题样本

- `minigeo_007`：raw output 先输出了一个可解析 JSON，随后又追加了 `</think>` 和第二段重复 JSON，导致 `thinking_raw_outputs=1/10` 与 `malformed_raw_json=1/10`。
- `minigeo_009`：gold evidence 为空，模型回答“当前证据不足”，但 raw JSON 中 `abstained=false`，因此造成 1 条 abstention 错误。

## 下一步

为了减少 A100 次数，暂时不跑新的训练。下一步优先在本地完成：

1. 把 evidence-conditioned json64 结果纳入主结果表和展示文档。
2. 离线检查 1 条 thinking 泄漏和 1 条 malformed JSON 的原始输出模式。
3. 只在本地修 prompt / parser / SFT 数据模板；除非本地审计明确通过，否则不再开启 A100。
