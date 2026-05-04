# MiniGeo SQL 评测

本报告记录 `data/benchmark/minigeo_bench.jsonl` 中 `requires_sql=true` 的 SQL 题评测结果。当前 benchmark 包含 60 条 SQL 题。

## 规则型 SQL baseline

运行：
```powershell
python scripts/evaluate_sql.py
```

结果：
```text
sql_items=60
sql_exec_accuracy=1.0
failures={}
```

## Qwen3.5-4B 模型 SQL generator

运行环境：

- Colab A100
- vLLM OpenAI-compatible API
- 模型：`Qwen/Qwen3.5-4B`
- Tunnel：Cloudflare quick tunnel
- `MINIGEO_DISABLE_THINKING=1`

运行：
```powershell
$env:OPENAI_BASE_URL="https://whose-intelligent-tips-copper.trycloudflare.com/v1"
$env:OPENAI_API_KEY="EMPTY"
$env:MINIGEO_MODEL="Qwen/Qwen3.5-4B"
$env:MINIGEO_DISABLE_THINKING="1"
python scripts/evaluate_sql.py --use-model
```

结果：
```text
sql_items=60
sql_exec_accuracy=1.0
failures={}
latency_ms=10180.943874999988
```

## 说明

- 当前结果基于 SQLite 演示数据库、SQL 执行器和 SQL 修复函数。
- 规则型 generator 与 Qwen3.5-4B 模型 generator 在当前 60 条 SQL benchmark 上均为 `sql_exec_accuracy=1.0`。
- 对于 `expected_result` 中的 `table` / `tables`，评测会同时检查 SQL 文本和执行结果。
