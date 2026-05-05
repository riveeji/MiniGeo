# MiniGeo QLoRA 1 Epoch Artifact Audit

本文件记录对 `F:\download-edge\minigeo_qlora_outputs.zip` 的本地检查结果。

## 结论

当前压缩包不能证明 1 epoch SFT 已完成。

压缩包中包含：

- `checkpoints/qlora-smoke/adapter/`
- `results/qlora_1epoch.md`
- `data/processed/sft_corpus.jsonl`

压缩包中未包含：

- `checkpoints/MiniGeo-Qwen3.5-2B-SFT-1epoch/adapter/`
- 1 epoch 训练的 `adapter_model.safetensors`
- 1 epoch 训练日志或 `trainer_state.json`

因此本次只能确认：

- Colab artifact 已包含一个 `Qwen/Qwen3.5-2B` LoRA adapter，但路径是 smoke adapter。
- SFT corpus 为 553 行，且与当前本地 `data/processed/sft_corpus.jsonl` 一致。
- 1 epoch SFT 仍应视为未完成或未成功打包，不能写入主结果表。

## Artifact

| Field | Value |
|---|---|
| Zip path | `F:\download-edge\minigeo_qlora_outputs.zip` |
| Zip SHA256 | `3C078DAB3A518D9FDB22A897482B788D63BA853CE635D01A06866201E6137DE8` |
| SFT rows | 553 |
| SFT corpus SHA256 | `9D73A45D05B918F755E9F006C33DC4DAF586D1DB6C673EBB2C2E3452B0F131F1` |
| Adapter found | `checkpoints/qlora-smoke/adapter` |
| 1 epoch adapter found | No |

## 下一步

下次 Colab A100 需要重新运行 1 epoch cell，并在下载前确认：

```bash
find checkpoints/MiniGeo-Qwen3.5-2B-SFT-1epoch/adapter -maxdepth 1 -type f | sort
```

必须看到 `adapter_config.json` 和 `adapter_model.safetensors` 后，再打包下载。
