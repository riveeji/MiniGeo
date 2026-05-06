# MiniGeo json64 Adapter Evidence-conditioned 复评 Cells

本文档用于复评已经训练好的 `MiniGeo-Qwen3.5-2B-SFT-json64step` adapter。json64 短训已证明 `thinking_raw_outputs=0/10`，但之前的 smoke prompt 没有注入 evidence block，导致 citation 评测不公平。当前仓库已经修正 `evaluate_sft_adapter.py`：默认会把 gold evidence chunk 放入 prompt。

本轮不训练，只重新加载 json64 adapter 做 evidence-conditioned smoke10。

## Cell 1：同步仓库

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
```

## Cell 3：上传 json64 zip

```python
from google.colab import files

uploaded = files.upload()
print(uploaded.keys())
```

上传：

```text
minigeo_json64_sft_smoke_outputs.zip
```

## Cell 4：解压并检查 adapter

```bash
%%bash
set -e

cd /content/MiniGeo

zip_path="/content/minigeo_json64_sft_smoke_outputs.zip"
if [ ! -f "$zip_path" ]; then
  echo "没有找到: $zip_path"
  find /content -maxdepth 1 -name "*.zip" -print
  exit 1
fi

unzip -o "$zip_path"

test -f checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter/adapter_config.json
test -f checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter/adapter_model.safetensors
```

## Cell 5：dry-run 确认 prompt 已包含 Evidence

```bash
%%bash
set -e

cd /content/MiniGeo
export PYTHONPATH=/content/MiniGeo/src

python scripts/evaluate_sft_adapter.py \
  --adapter-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-json64step/adapter \
  --limit 2 \
  --output results/sft_adapter_json64_evidence_dryrun.jsonl \
  --report results/sft_adapter_json64_evidence_dryrun.md \
  --dry-run

python - <<'PY'
import json
from pathlib import Path

records = [json.loads(line) for line in Path("results/sft_adapter_json64_evidence_dryrun.jsonl").read_text(encoding="utf-8").splitlines()]
for record in records:
    assert "Evidence:" in record["prompt"], record["id"]
    assert "citations must use only these chunk_id values" in record["prompt"], record["id"]
print("prompt evidence check passed")
PY
```

## Cell 6：evidence-conditioned smoke10

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
  --output results/sft_adapter_json64_evidence_smoke10.jsonl \
  --report results/sft_adapter_json64_evidence_smoke10.md
```

## Cell 7：重解析并统计格式

```bash
%%bash
set -e

cd /content/MiniGeo
export PYTHONPATH=/content/MiniGeo/src

python scripts/reparse_sft_adapter_outputs.py \
  --input results/sft_adapter_json64_evidence_smoke10.jsonl \
  --output results/sft_adapter_json64_evidence_smoke10_reparsed.jsonl \
  --report results/sft_adapter_json64_evidence_smoke10_reparsed.md

python - <<'PY'
import json
from pathlib import Path

records = [json.loads(line) for line in Path("results/sft_adapter_json64_evidence_smoke10.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
thinking = sum("</think>" in str(row.get("result", {}).get("raw_model_output", "")) for row in records)
malformed = 0
empty_citations = 0
for row in records:
    raw = str(row.get("result", {}).get("raw_model_output", "")).strip()
    try:
        json.loads(raw)
    except json.JSONDecodeError:
        malformed += 1
    if '"citations":[]' in raw:
        empty_citations += 1

report = [
    "# MiniGeo json64 Evidence-conditioned Smoke10",
    "",
    Path("results/sft_adapter_json64_evidence_smoke10_reparsed.md").read_text(encoding="utf-8"),
    "",
    "## Format Diagnostics",
    "",
    f"- thinking_raw_outputs={thinking}",
    f"- malformed_raw_json={malformed}",
    f"- empty_citations_raw={empty_citations}",
]
Path("results/sft_adapter_json64_evidence_summary.md").write_text("\n".join(report), encoding="utf-8", newline="\n")
print("thinking_raw_outputs=", thinking)
print("malformed_raw_json=", malformed)
print("empty_citations_raw=", empty_citations)
PY
```

## Cell 8：打包下载

```bash
%%bash
set -e

cd /content/MiniGeo

zip -r /content/minigeo_json64_evidence_eval_outputs.zip \
  results/sft_adapter_json64_evidence_dryrun.jsonl \
  results/sft_adapter_json64_evidence_dryrun.md \
  results/sft_adapter_json64_evidence_smoke10.jsonl \
  results/sft_adapter_json64_evidence_smoke10.md \
  results/sft_adapter_json64_evidence_smoke10_reparsed.jsonl \
  results/sft_adapter_json64_evidence_smoke10_reparsed.md \
  results/sft_adapter_json64_evidence_summary.md

ls -lh /content/minigeo_json64_evidence_eval_outputs.zip
```

```python
from google.colab import files

files.download("/content/minigeo_json64_evidence_eval_outputs.zip")
```
