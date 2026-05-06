# MiniGeo JSON-only SFT 短训 Cells

本文档用于下一次 Colab A100：使用已修订的 JSON-only SFT corpus 重新做一轮短 QLoRA/SFT smoke，并检查 `</think>` 泄漏是否下降。不要直接跑 1 epoch；先用 64 step 验证格式修复是否有效。

## 目标

- 使用最新 GitHub 仓库中的 `data/processed/sft_corpus.jsonl`。
- 确认 SFT 输出全是单 JSON 对象，且没有 `<think>` / `</think>`。
- 训练一个短 run：`MiniGeo-Qwen3.5-2B-SFT-json64step`。
- 在同一 10 题 smoke 子集上评测新 adapter。
- 打包 adapter 和评测结果，下载后本地导入。

## Cell 0：确认 A100

```python
import torch

print("cuda_available=", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu=", torch.cuda.get_device_name(0))
```

## Cell 1：同步最新仓库

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
if torch.cuda.is_available():
    print("gpu=", torch.cuda.get_device_name(0))
PY
```

## Cell 3：重建并检查 JSON-only SFT corpus

```bash
%%bash
set -e

cd /content/MiniGeo
export PYTHONPATH=/content/MiniGeo/src

python scripts/build_sft_corpus.py

python - <<'PY'
import json
from pathlib import Path

rows = [json.loads(line) for line in Path("data/processed/sft_corpus.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
bad = []
for row in rows:
    output = row["output"]
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as exc:
        bad.append((row["id"], f"json_error={exc}"))
        continue
    if set(parsed) != {"answer", "citations", "abstained", "confidence"}:
        bad.append((row["id"], "bad_keys"))
    if "<think" in output.lower() or "</think>" in output.lower():
        bad.append((row["id"], "thinking_tag"))
    if output.count("{") != 1 or output.count("}") != 1:
        bad.append((row["id"], "multi_json_or_nested_object"))

print("rows=", len(rows))
print("bad=", bad[:10])
if bad:
    raise SystemExit(1)
PY
```

## Cell 4：64 step 短训

```bash
%%bash
set -e

cd /content/MiniGeo
export PYTHONPATH=/content/MiniGeo/src
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

python scripts/run_qlora_smoke.py \
  --sample-size 128 \
  --max-steps 64 \
  --output-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step
```

## Cell 5：检查 adapter

```bash
%%bash
set -e

cd /content/MiniGeo

test -f checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter/adapter_config.json
test -f checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter/adapter_model.safetensors

find checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter -maxdepth 1 -type f | sort
```

## Cell 6：评测新 adapter smoke10

```bash
%%bash
set -e

cd /content/MiniGeo
export PYTHONPATH=/content/MiniGeo/src
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

python scripts/evaluate_sft_adapter.py \
  --adapter-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter \
  --base-model Qwen/Qwen3.5-2B \
  --limit 10 \
  --max-new-tokens 256 \
  --output results/sft_adapter_json64_smoke10.jsonl \
  --report results/sft_adapter_json64_smoke10.md
```

## Cell 7：重解析并统计 thinking 泄漏

```bash
%%bash
set -e

cd /content/MiniGeo
export PYTHONPATH=/content/MiniGeo/src

python scripts/reparse_sft_adapter_outputs.py \
  --input results/sft_adapter_json64_smoke10.jsonl \
  --output results/sft_adapter_json64_smoke10_reparsed.jsonl \
  --report results/sft_adapter_json64_smoke10_reparsed.md

python - <<'PY'
import json
from pathlib import Path

records = [json.loads(line) for line in Path("results/sft_adapter_json64_smoke10.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
thinking = sum("</think>" in str(row.get("result", {}).get("raw_model_output", "")) for row in records)
multi_json = sum(str(row.get("result", {}).get("raw_model_output", "")).count("{") > 1 for row in records)

summary = [
    "# MiniGeo JSON-only SFT json64 Smoke Summary",
    "",
    Path("results/sft_adapter_json64_smoke10.md").read_text(encoding="utf-8"),
    "",
    "## Format Diagnostics",
    "",
    f"- thinking_raw_outputs={thinking}",
    f"- multi_json_raw_outputs={multi_json}",
    "",
    "## Decision",
    "",
    "- 若 thinking_raw_outputs 明显低于旧 128step 的 7/10，且 citation/refusal 不退化，可继续扩大到 128 或 553 step。",
    "- 若 thinking 仍高，继续修 chat template 或训练文本，不跑 1 epoch。",
]
Path("results/sft_adapter_json64_summary.md").write_text("\n".join(summary), encoding="utf-8", newline="\n")
print("thinking_raw_outputs=", thinking)
print("multi_json_raw_outputs=", multi_json)
print("wrote=results/sft_adapter_json64_summary.md")
PY
```

## Cell 8：打包下载

```bash
%%bash
set -e

cd /content/MiniGeo

test -f checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter/adapter_model.safetensors
test -f results/sft_adapter_json64_smoke10.jsonl
test -f results/sft_adapter_json64_smoke10.md
test -f results/sft_adapter_json64_smoke10_reparsed.jsonl
test -f results/sft_adapter_json64_smoke10_reparsed.md
test -f results/sft_adapter_json64_summary.md

zip -r /content/minigeo_json64_sft_smoke_outputs.zip \
  checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter \
  data/processed/sft_corpus.jsonl \
  results/sft_adapter_json64_smoke10.jsonl \
  results/sft_adapter_json64_smoke10.md \
  results/sft_adapter_json64_smoke10_reparsed.jsonl \
  results/sft_adapter_json64_smoke10_reparsed.md \
  results/sft_adapter_json64_summary.md

ls -lh /content/minigeo_json64_sft_smoke_outputs.zip
```

```python
from google.colab import files

files.download("/content/minigeo_json64_sft_smoke_outputs.zip")
```

下载完成后即可关闭 A100。
