# MiniGeo SFT Adapter 评测 Runbook

本文件用于在 Colab A100 上加载 `MiniGeo-Qwen3.5-2B-SFT-128step` LoRA adapter，并运行小规模推理 smoke test。

## 前提

- 已下载或保留 `minigeo_qlora_outputs_128step.zip`。
- zip 中必须包含 `checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter/adapter_model.safetensors`。
- 本评测只验证 adapter 可加载、可生成、能否遵守 JSON 输出格式；不是最终 SFT 质量结论。

## Colab Cells

### Cell 1：同步仓库

```bash
%%bash
set -e

cd /content

if [ ! -d MiniGeo/.git ]; then
  git clone https://github.com/riveeji/MiniGeo.git MiniGeo
else
  cd /content/MiniGeo
  git restore results/qlora_1epoch.md README.md docs/project-showcase.md || true
  git pull --ff-only origin main
fi

cd /content/MiniGeo
git status --short --branch
git rev-parse --short HEAD
```

### Cell 2：安装依赖

```bash
%%bash
set -e

cd /content/MiniGeo

python -m pip install -U pip setuptools wheel
python -m pip install -r requirements-dev.txt
python -m pip install -U transformers accelerate peft bitsandbytes datasets sentencepiece safetensors
```

### Cell 3：上传并解压 128step artifact

先用 Colab 文件面板上传 `minigeo_qlora_outputs_128step.zip` 到 `/content/`，再执行：

```bash
%%bash
set -e

cd /content/MiniGeo
unzip -o /content/minigeo_qlora_outputs_128step.zip

find checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter -maxdepth 1 -type f | sort
```

### Cell 4：只检查 adapter 文件

```bash
%%bash
set -e

cd /content/MiniGeo

python scripts/evaluate_sft_adapter.py \
  --adapter-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter \
  --check-only
```

### Cell 5：dry-run 检查 prompt 和输出路径

```bash
%%bash
set -e

cd /content/MiniGeo

python scripts/evaluate_sft_adapter.py \
  --adapter-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter \
  --limit 5 \
  --output results/sft_adapter_128step_dryrun.jsonl \
  --report results/sft_adapter_128step_dryrun.md \
  --dry-run
```

### Cell 6：真实加载 adapter 跑 10 题 smoke

```bash
%%bash
set -e

cd /content/MiniGeo

python scripts/evaluate_sft_adapter.py \
  --adapter-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter \
  --base-model Qwen/Qwen3.5-2B \
  --limit 10 \
  --max-new-tokens 256 \
  --output results/sft_adapter_128step_smoke10.jsonl \
  --report results/sft_adapter_128step_smoke10.md
```

### Cell 7：打包评测输出

```bash
%%bash
set -e

cd /content/MiniGeo

test -f results/sft_adapter_128step_smoke10.jsonl
test -f results/sft_adapter_128step_smoke10.md
test -f results/sft_adapter_128step_dryrun.jsonl
test -f results/sft_adapter_128step_dryrun.md

zip -r /content/minigeo_sft_adapter_eval_128step.zip \
  results/sft_adapter_128step_smoke10.jsonl \
  results/sft_adapter_128step_smoke10.md \
  results/sft_adapter_128step_dryrun.jsonl \
  results/sft_adapter_128step_dryrun.md

ls -lh /content/minigeo_sft_adapter_eval_128step.zip
```

### Cell 8：下载结果

```python
from google.colab import files
files.download("/content/minigeo_sft_adapter_eval_128step.zip")
```

## 通过标准

- `--check-only` 没有 adapter 文件缺失。
- 打包 cell 必须先通过 `test -f results/sft_adapter_128step_smoke10.jsonl` 和 `test -f results/sft_adapter_128step_smoke10.md`。
- `results/sft_adapter_128step_smoke10.md` 中 `request_errors=0`。
- `non_empty_answer_rate` 不为 0。
- 输出 JSON 中没有大段 thinking process。

## 后续

如果 smoke10 正常，再扩大到 50 题，并与 base model no-RAG/RAG 结果并列表比较。
