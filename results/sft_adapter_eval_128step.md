# MiniGeo SFT Adapter 128step Evaluation Artifact Audit

本文件记录对 `F:\download-edge\minigeo_sft_adapter_eval_128step.zip` 的本地检查结果。

## 结论

当前压缩包只包含 dry-run 输出，不能证明 128step SFT adapter 已完成真实推理 smoke test。

压缩包中包含：

- `results/sft_adapter_128step_dryrun.jsonl`
- `results/sft_adapter_128step_dryrun.md`

压缩包中未包含：

- `results/sft_adapter_128step_smoke10.jsonl`
- `results/sft_adapter_128step_smoke10.md`

因此本次只能确认：

- Colab 已能生成 dry-run prompt 和报告。
- dry-run 选中了 5 条 benchmark 样例。
- 真实加载 `Qwen/Qwen3.5-2B` + 128step LoRA adapter 的 Cell 9 没有成功产出可审计结果，或打包前结果文件不存在。
- 当前不能计算 SFT adapter 的 `non_empty_answer_rate`、`citation_hit_rate` 或 `abstention_accuracy`。

## Artifact

| Field | Value |
|---|---|
| Zip path | `F:\download-edge\minigeo_sft_adapter_eval_128step.zip` |
| Zip SHA256 | `6CBF2CC11D7F15C9FB922D2EE8CBA178A135E3B8309F74FBDC4C9756979F05AA` |
| Zip size | 1573 bytes |
| Dry-run records | 5 |
| Smoke10 records found | No |
| Smoke10 report found | No |

## 下一步

回到 Colab 后，重新运行真实 smoke cell：

```bash
python scripts/evaluate_sft_adapter.py \
  --adapter-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter \
  --base-model Qwen/Qwen3.5-2B \
  --limit 10 \
  --max-new-tokens 256 \
  --output results/sft_adapter_128step_smoke10.jsonl \
  --report results/sft_adapter_128step_smoke10.md
```

打包前必须确认：

```bash
test -f results/sft_adapter_128step_smoke10.jsonl
test -f results/sft_adapter_128step_smoke10.md
```
