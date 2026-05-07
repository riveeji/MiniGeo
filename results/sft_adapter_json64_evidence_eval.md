# MiniGeo json64 Evidence-conditioned SFT 复评

本文记录对 `F:\download-edge\minigeo_json64_evidence_eval_outputs.zip` 和最终复核包 `F:\download-edge\minigeo_json64_evidence_final_smoke_outputs.zip` 的本地接入结果。

## 结论

json64 adapter 在注入 gold evidence block 后，citation 行为明显恢复：`citation_hit_rate=1.000`。最终 A100 短 smoke 中，`abstention_accuracy=1.000`，`thinking_raw_outputs=0/10`，原始尾部污染从上一轮的 1/10 降到 0/10。

这说明上一轮闭卷 json64 smoke 的 citation 失败主要来自评测 prompt 没有提供 evidence，而不是 adapter 完全丧失引用能力。但该结果仍不直接支持长训：最终 smoke 仍有 1/10 malformed raw JSON（`minigeo_009` 中出现 `" "abstained"` 键名前缀错误），说明格式稳定性还没有完全解决。

| System | citation_hit_rate | abstention_accuracy | thinking_raw_outputs | malformed_raw_json | empty_citations_raw |
|---|---:|---:|---:|---:|---:|
| MiniGeo-2B-SFT json64 smoke10 closed-book | 0.000 | 0.100 | 0/10 | 8/10 | 9/10 |
| MiniGeo-2B-SFT json64 evidence smoke10 reparsed | 1.000 | 1.000 | 0/10 | 1/10 | 1/10 |

## 导入文件

- `results/sft_adapter_json64_evidence_dryrun.jsonl`
- `results/sft_adapter_json64_evidence_dryrun.md`
- `results/sft_adapter_json64_evidence_smoke10.jsonl`
- `results/sft_adapter_json64_evidence_smoke10.md`
- `results/sft_adapter_json64_evidence_smoke10_reparsed.jsonl`
- `results/sft_adapter_json64_evidence_smoke10_reparsed.md`
- `results/sft_adapter_json64_evidence_summary.md`

## 问题样本

- 上一轮 `minigeo_007`：原始 raw output 先输出了一个可解析 JSON，随后又追加了 `</think>` 和第二段重复 JSON；最终 smoke 中该类尾部污染未再出现。
- 最终 smoke `minigeo_009`：gold evidence 为空，语义上正确拒答，但 raw JSON 中出现 `" "abstained"` 键名前缀错误，导致 official raw JSON 仍有 1/10 malformed。

## 下一步

为了减少 A100 次数，暂时不跑新的训练。下一步优先在本地完成：

1. 暂不继续长训；先把 malformed raw JSON 作为 SFT 格式问题记录到最终材料。
2. 后续如继续训练，优先补充 malformed JSON 修复样本，而不是扩大训练步数。
