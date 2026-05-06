# MiniGeo 下一轮 A100 顺序执行 Cells

> 该文档记录 base 2B vs SFT 128step 对照流程。该对照已经在 2026-05-06 跑完，结果见 `results/base_vs_sft_128step_smoke10.md`。如果要继续验证 JSON-only SFT 格式修复，请使用 `docs/a100-json-sft-smoke-cells.md`。

本文档用于下一次开启 Colab A100 时，按顺序完成 `Qwen/Qwen3.5-2B` base 与 `MiniGeo-Qwen3.5-2B-SFT-128step` adapter 的同题 smoke 对照。Colab 不能并行执行两个长期 cell，因此下面所有步骤都设计为串行运行。

## 目标

- 重新同步干净仓库，避免 Colab 旧输出阻塞 `git pull`。
- 安装能识别 `qwen3_5` 架构的 Transformers 环境。
- 加载同一 10 题 smoke 子集，分别跑 base 2B 与 128step SFT adapter。
- 离线重解析 SFT 输出，生成 base/SFT 对照材料。
- 打包下载结果，A100 跑完后即可关闭。

## Cell 0：确认 GPU

```python
import torch

print("cuda_available=", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device=", torch.cuda.get_device_name(0))
    print("capability=", torch.cuda.get_device_capability(0))
```

期望输出里包含 `A100`。如果不是 A100，也可以跑 2B smoke，但速度和显存余量会变差。

## Cell 1：同步干净仓库

这个 cell 不直接 `git pull` 旧目录，而是把旧的 `/content/MiniGeo` 备份后重新 clone，避免之前遇到的 `results/*.md` 或未跟踪文件阻塞合并。

```bash
%%bash
set -e

cd /content

if [ -d MiniGeo ]; then
  stamp=$(date +%Y%m%d_%H%M%S)
  mv MiniGeo "MiniGeo_backup_${stamp}"
  echo "旧目录已备份到 /content/MiniGeo_backup_${stamp}"
fi

git clone https://github.com/riveeji/MiniGeo.git MiniGeo

cd /content/MiniGeo
git status --short --branch
git rev-parse --short HEAD
```

## Cell 2：安装依赖

使用 `python -m pip`，不要直接写 `pip install ...`，避免在 Python cell 中触发 `SyntaxError`。这里从 GitHub 安装 Transformers，是为了规避 Colab 默认版本不识别 `model_type=qwen3_5` 的问题。

```bash
%%bash
set -e

cd /content/MiniGeo

python -m pip install -U pip setuptools wheel
python -m pip install -e .
python -m pip install -U accelerate peft bitsandbytes datasets sentencepiece safetensors
python -m pip install -U git+https://github.com/huggingface/transformers.git

python - <<'PY'
import transformers
import torch
print("transformers=", transformers.__version__)
print("torch=", torch.__version__)
print("cuda=", torch.cuda.is_available())
PY
```

## Cell 3：上传并解压 128step adapter

先运行这个 Python cell，选择本地的 `minigeo_qlora_outputs_128step.zip`。

```python
from google.colab import files

uploaded = files.upload()
print(uploaded.keys())
```

然后运行解压 cell：

```bash
%%bash
set -e

cd /content/MiniGeo

zip_path=$(find /content -maxdepth 1 -name "minigeo_qlora_outputs_128step*.zip" | head -n 1)
if [ -z "$zip_path" ]; then
  echo "没有找到 /content/minigeo_qlora_outputs_128step*.zip"
  exit 1
fi

echo "使用 artifact: $zip_path"
unzip -o "$zip_path"

test -f checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter/adapter_config.json
test -f checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter/adapter_model.safetensors

find checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter -maxdepth 1 -type f | sort
```

## Cell 4：本地脚本 dry-run

这个 cell 不加载模型，只检查 benchmark 子集、prompt、输出路径和 adapter 文件。

```bash
%%bash
set -e

cd /content/MiniGeo
export PYTHONPATH=/content/MiniGeo/src

python scripts/evaluate_sft_adapter.py \
  --adapter-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter \
  --check-only

python scripts/evaluate_base_model.py \
  --base-model Qwen/Qwen3.5-2B \
  --limit 5 \
  --output results/base_qwen35_2b_dryrun.jsonl \
  --report results/base_qwen35_2b_dryrun.md \
  --dry-run

python scripts/evaluate_sft_adapter.py \
  --adapter-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter \
  --limit 5 \
  --output results/sft_adapter_128step_dryrun.jsonl \
  --report results/sft_adapter_128step_dryrun.md \
  --dry-run
```

## Cell 5：跑 base 2B smoke10

```bash
%%bash
set -e

cd /content/MiniGeo
export PYTHONPATH=/content/MiniGeo/src
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

python scripts/evaluate_base_model.py \
  --base-model Qwen/Qwen3.5-2B \
  --limit 10 \
  --max-new-tokens 256 \
  --output results/base_qwen35_2b_smoke10.jsonl \
  --report results/base_qwen35_2b_smoke10.md
```

## Cell 6：跑 SFT 128step adapter smoke10

```bash
%%bash
set -e

cd /content/MiniGeo
export PYTHONPATH=/content/MiniGeo/src
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

python scripts/evaluate_sft_adapter.py \
  --adapter-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter \
  --base-model Qwen/Qwen3.5-2B \
  --limit 10 \
  --max-new-tokens 256 \
  --output results/sft_adapter_128step_smoke10.jsonl \
  --report results/sft_adapter_128step_smoke10.md
```

## Cell 7：重解析 SFT 输出并生成对照摘要

```bash
%%bash
set -e

cd /content/MiniGeo
export PYTHONPATH=/content/MiniGeo/src

python scripts/reparse_sft_adapter_outputs.py \
  --input results/sft_adapter_128step_smoke10.jsonl \
  --output results/sft_adapter_128step_smoke10_reparsed.jsonl \
  --report results/sft_adapter_128step_smoke10_reparsed.md

python - <<'PY'
from pathlib import Path

base = Path("results/base_qwen35_2b_smoke10.md").read_text(encoding="utf-8")
sft = Path("results/sft_adapter_128step_smoke10_reparsed.md").read_text(encoding="utf-8")

report = [
    "# Base 2B vs SFT 128step Smoke10 对照",
    "",
    "## Base 2B",
    "",
    base,
    "",
    "## SFT 128step Reparsed",
    "",
    sft,
    "",
    "## 判读规则",
    "",
    "- 如果 SFT 的 citation_hit_rate、abstention_accuracy 或 JSON 格式明显优于 base，再考虑 553step 或 1 epoch。",
    "- 如果 SFT 仍大量输出 `</think>` 或多 JSON，先修训练样本格式和 prompt，不继续长训。",
]

Path("results/base_vs_sft_128step_smoke10.md").write_text("\n".join(report), encoding="utf-8", newline="\n")
print("wrote=results/base_vs_sft_128step_smoke10.md")
PY
```

## Cell 8：打包下载结果

```bash
%%bash
set -e

cd /content/MiniGeo

test -f results/base_qwen35_2b_smoke10.jsonl
test -f results/base_qwen35_2b_smoke10.md
test -f results/sft_adapter_128step_smoke10.jsonl
test -f results/sft_adapter_128step_smoke10.md
test -f results/sft_adapter_128step_smoke10_reparsed.jsonl
test -f results/sft_adapter_128step_smoke10_reparsed.md
test -f results/base_vs_sft_128step_smoke10.md

zip -r /content/minigeo_base_vs_sft_128step_smoke10.zip \
  results/base_qwen35_2b_smoke10.jsonl \
  results/base_qwen35_2b_smoke10.md \
  results/sft_adapter_128step_smoke10.jsonl \
  results/sft_adapter_128step_smoke10.md \
  results/sft_adapter_128step_smoke10_reparsed.jsonl \
  results/sft_adapter_128step_smoke10_reparsed.md \
  results/base_vs_sft_128step_smoke10.md

ls -lh /content/minigeo_base_vs_sft_128step_smoke10.zip
```

```python
from google.colab import files

files.download("/content/minigeo_base_vs_sft_128step_smoke10.zip")
```

## 关掉 A100 前检查

下载 zip 后，再确认文件大小不是 0：

```bash
%%bash
ls -lh /content/minigeo_base_vs_sft_128step_smoke10.zip
```

确认 zip 已下载到本地后，就可以断开 Colab runtime，关闭 A100。

## 通过标准

- `results/base_qwen35_2b_smoke10.md` 存在。
- `results/sft_adapter_128step_smoke10_reparsed.md` 存在。
- 两边 `request_errors=0`。
- SFT 原始输出中的 `</think>` 数量不能继续扩大。
- 若 SFT 没有优于 base，则停止长训，先改 SFT 数据和输出模板。
