# MiniGeo QLoRA Smoke Run

本报告记录 2026-05-04 在 Colab A100 上完成的 QLoRA smoke run。该 run 只验证训练链路、依赖、显存和数据格式，不作为正式 SFT 结果。

## 配置

| Field | Value |
|---|---|
| Base model | `Qwen/Qwen3.5-2B` |
| Train data | `data/processed/sft_corpus.jsonl` |
| Sample size | 32 |
| Max steps | 5 |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |
| Learning rate | 0.0002 |
| Output dir | `checkpoints/qlora-smoke` |

## 结果

```text
items=135
reference_answer_leaks=[]
trainable params: 10,911,744
all params: 1,892,736,832
trainable%: 0.5765
train_runtime: 7.047
train_loss: 2.663
wrote=checkpoints/qlora-smoke/adapter
```

## 结论

- `Qwen/Qwen3.5-2B` 能在 Colab A100 上加载。
- 4-bit QLoRA + LoRA adapter 链路能完成 5 个训练 step。
- `data/processed/sft_corpus.jsonl` 的数据格式可用于训练。
- Adapter 已本地归档到 `checkpoints/qlora-smoke/adapter`，但 checkpoint 文件不提交到 Git。

## 下一步

正式 SFT 前应先决定：

- 是否沿用 32 条 smoke 样本的 prompt 格式。
- 是否扩充 SFT corpus 的任务类型和真实答案样本。
- 是否运行更长的 1 epoch 小规模 SFT，并补充 base / SFT / RAG / Verifier 对照评测。
