# MiniGeo QLoRA 128 Step Run

本文件记录对 `F:\download-edge\minigeo_qlora_outputs_128step.zip` 的本地检查结果。

## 结论

128 step 小规模 QLoRA/SFT 产物已生成并通过 artifact 检查。

压缩包中包含：

- `checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter/adapter_config.json`
- `checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter/adapter_model.safetensors`
- `checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter/tokenizer.json`
- `checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter/tokenizer_config.json`
- `checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter/chat_template.jinja`
- `results/qlora_128step.md`
- `data/processed/sft_corpus.jsonl`

因此本次可以确认：

- `Qwen/Qwen3.5-2B` 的 4-bit QLoRA 训练链路能完成 128 step。
- LoRA adapter 已成功保存到 `checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter`。
- SFT corpus 为 553 行。
- 当前结果只证明训练产物生成，不代表 SFT 模型质量已经提升；后续仍需加载 adapter 做 base / SFT / RAG / Verifier 对照评测。

## Colab Report

```text
Time: 2026-05-05T07:20:44.984290Z
Runtime: Colab A100
Base model: Qwen/Qwen3.5-2B
Train data: data/processed/sft_corpus.jsonl
Train rows available: 553
Sample size: 128
Max steps: 128
Method: 4-bit QLoRA
Output: checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter
Status: PASS: adapter_model.safetensors found.
```

## Artifact

| Field | Value |
|---|---|
| Zip path | `F:\download-edge\minigeo_qlora_outputs_128step.zip` |
| Zip SHA256 | `5163A761ABE1F06D50A1AF659AC31A08974F294BB0E8F1D7B1227EC61001E8E5` |
| SFT rows | 553 |
| Adapter path | `checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter` |
| Adapter config found | Yes |
| Adapter weights found | Yes |
| Base model | `Qwen/Qwen3.5-2B` |
| PEFT type | LoRA |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |

## 下一步

1. 在 Colab 或本地 GPU 环境加载 `Qwen/Qwen3.5-2B` + 128step adapter，运行小规模生成 smoke。
2. 在同一 MiniGeo-Bench 子集上比较 base 与 SFT 的 answer format、refusal 和 citation behavior。
3. 若 128step 结果稳定，再考虑运行 553step 或 1 epoch。
