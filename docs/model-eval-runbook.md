# MiniGeo 模型评测 Runbook

本文件用于下次开启 Colab A100 时执行 Phase 1/Phase 2。原则是先用 10 题 smoke test 验证 JSON-only 输出，再跑 150 题或 300 题正式评测。

## 目标

- 修复并验证 `Thinking Process` 泄漏。
- 先跑 10 题 smoke test，确认输出质量达标。
- 再跑 150 题或 300 题 `Qwen3.5-4B no-RAG` 与 `Qwen3.5-4B + BM25 RAG` 对照。
- 所有长任务都使用逐题落盘与 resume，避免 Cloudflare tunnel 抖动导致整批结果丢失。

## Colab 服务要求

Colab A100 上启动 vLLM OpenAI-compatible 服务，模型建议：

```text
Qwen/Qwen3.5-4B
```

服务启动后，通过 Cloudflare quick tunnel 暴露本地 `http://localhost:8000`，拿到类似下面的地址：

```text
https://your-tunnel.trycloudflare.com
```

本地 PowerShell 统一使用：

```powershell
$env:OPENAI_BASE_URL="https://your-tunnel.trycloudflare.com/v1"
$env:OPENAI_API_KEY="EMPTY"
$env:MINIGEO_MODEL="Qwen/Qwen3.5-4B"
$env:MINIGEO_LLM_TIMEOUT="180"
$env:MINIGEO_LLM_RETRIES="5"
$env:MINIGEO_DISABLE_THINKING="1"
```

## Step 1：连通性检查

```powershell
Invoke-WebRequest -Uri "$env:OPENAI_BASE_URL/models" -UseBasicParsing -TimeoutSec 30
```

确认返回模型列表后再继续。

## Step 2：10 题 smoke test

```powershell
python scripts/evaluate_model_service.py `
  --limit 10 `
  --selection evidence `
  --mode both `
  --output results/model_service_qwen35_4b_smoke10.jsonl `
  --no-resume
```

然后生成输出质量审计：

```powershell
python scripts/audit_model_outputs.py `
  --rag results/model_service_qwen35_4b_smoke10_rag.jsonl `
  --no-rag results/model_service_qwen35_4b_smoke10_no_rag.jsonl `
  --output results/model_output_quality_smoke10.md
```

通过标准：

- `Request Errors = 0`
- `Placeholder Answer = 0`
- `Thinking Answer` 尽量接近 `0`
- RAG 的 `Citation Miss` 不能明显高于当前 30 题结果的 `0.167`

如果 smoke test 仍然大量输出 `Thinking Process`，停止，不要跑 150 题；优先调整 vLLM chat template 或模型启动参数。

## Step 3：150 题正式评测

```powershell
python scripts/evaluate_model_service.py `
  --limit 150 `
  --selection all `
  --mode both `
  --output results/model_service_qwen35_4b_150.jsonl `
  --no-resume
```

如果中途断线或 Colab tunnel 抖动，去掉 `--no-resume` 重新执行同一命令即可从已完成题目继续：

```powershell
python scripts/evaluate_model_service.py `
  --limit 150 `
  --selection all `
  --mode both `
  --output results/model_service_qwen35_4b_150.jsonl
```

如果 A100 时间充足，并且 150 题结果稳定，可以直接跑 300 题全量 benchmark：

```powershell
python scripts/evaluate_model_service.py `
  --limit 300 `
  --selection all `
  --mode both `
  --output results/model_service_qwen35_4b_300.jsonl `
  --no-resume
```

中断后同样去掉 `--no-resume` 继续。

## Step 4：150 题质量审计

```powershell
python scripts/audit_model_outputs.py `
  --rag results/model_service_qwen35_4b_150_rag.jsonl `
  --no-rag results/model_service_qwen35_4b_150_no_rag.jsonl `
  --output results/model_output_quality_150.md
```

300 题质量审计命令：

```powershell
python scripts/audit_model_outputs.py `
  --rag results/model_service_qwen35_4b_300_rag.jsonl `
  --no-rag results/model_service_qwen35_4b_300_no_rag.jsonl `
  --output results/model_output_quality_300.md
```

## Step 5：失败归因分析

```powershell
python scripts/analyze_model_failures.py `
  --input results/model_service_qwen35_4b_150_rag.jsonl `
  --output results/model_failure_analysis_150.md
```

300 题失败归因命令：

```powershell
python scripts/analyze_model_failures.py `
  --input results/model_service_qwen35_4b_300_rag.jsonl `
  --output results/model_failure_analysis_300.md
```

重点先看 `model_cited_other` 和 `model_cited_neighbor`。前者通常说明模型没有严格引用 gold evidence；后者通常说明 chunk 粒度或 evidence label 需要人工抽检。

## Step 6：导出人工抽检表

```powershell
python scripts/export_failure_review.py `
  --input results/model_service_qwen35_4b_150_rag.jsonl `
  --csv-output results/model_failure_review_150.csv `
  --markdown-output results/model_failure_review_150.md
```

默认只导出 `model_cited_neighbor` 和 `model_cited_other`。如果要导出全部 citation miss：

```powershell
python scripts/export_failure_review.py `
  --categories all
```

CSV 中的 `review_decision` 建议使用 `model_error`、`label_expand`、`retrieval_error` 或 `ambiguous`。其中 `label_expand` 表示模型引用的 chunk 也能支撑答案，应扩充 benchmark evidence label。

## Step 7：离线运行 RAG + Verifier

```powershell
python scripts/evaluate_verified_model_service.py `
  --input results/model_service_qwen35_4b_150_rag.jsonl `
  --output results/model_service_qwen35_4b_150_rag_verified.jsonl `
  --report results/model_service_verified_eval_150.md
```

默认使用本地 heuristic Verifier，不会调用模型服务。如果要使用模型辅助 Verifier：

```powershell
$env:MINIGEO_VERIFIER_BASE_URL="https://your-tunnel.trycloudflare.com/v1"
$env:MINIGEO_VERIFIER_API_KEY="EMPTY"
$env:MINIGEO_VERIFIER_MODEL="Qwen/Qwen3.5-4B"
python scripts/evaluate_verified_model_service.py --use-model
```

离线 Verifier 会保留 `verification` 报告；如果答案不是 `supported`，会把最终结果改为拒答，并把原始回答保存在 `unverified_answer`。

## Step 8：导出 Verifier 拦截样例

```powershell
python scripts/export_verifier_interceptions.py `
  --input results/model_service_qwen35_4b_150_rag_verified.jsonl `
  --csv-output results/verifier_interceptions_150.csv `
  --markdown-output results/verifier_interceptions_150.md
```

CSV 中的 `review_decision` 建议使用 `correct_reject`、`false_reject`、`claim_split_error` 或 `needs_model_verifier`。如果剩余样例需要模型辅助复判，再等 A100 开启后用 `evaluate_verified_model_service.py --use-model`。

## Step 9：结果入表

评测结束后更新：

- `results/main_results.md`
- `results/model_service_eval.md`
- `results/model_output_quality_150.md`
- `results/model_failure_analysis_150.md`
- `results/model_failure_review_150.md`
- `results/model_service_verified_eval_150.md`
- `results/verifier_interceptions_150.md`
- `results/retrieval_service_eval.md`
- `results/failure_cases.md`

主表至少记录：

- `Qwen3.5-4B no-RAG`
- `Qwen3.5-4B + BM25 RAG`
- Citation Hit
- Abstention
- Latency
- Request Errors

检索服务消融完成后，额外记录：

- `Qwen3-Embedding dense retrieval`
- `Qwen3-Embedding hybrid retrieval`
- `Qwen3-Embedding hybrid + lexical rerank`
- `Qwen3-Reranker` staged 或 combined 消融结果

推荐运行时直接写报告文件：

```powershell
python scripts/evaluate_retrieval_ablation.py --use-embedding-service --json-output results/retrieval_service_eval.json --markdown-output results/retrieval_service_eval.md
python scripts/evaluate_retrieval_ablation.py --use-reranker-service --json-output results/retrieval_service_eval.json --markdown-output results/retrieval_service_eval.md
```

## 当前注意事项

- 当前 parser 会归一化 `"[doc_id#chunk_id]"` 形式的 citation。
- 当前 prompt 已加入 `/no_think` 和 JSON API system message；本地 client 还会在 `MINIGEO_DISABLE_THINKING=1` 时向 vLLM 发送 `chat_template_kwargs={"enable_thinking": false}`。
- 当前 RAG prompt 要求 citation 必须直接支撑答案；非系统类问题如果模型引用泛化 `doc_system` chunk，本地后处理会过滤这类系统引用，或在只引用系统 chunk 时改为与答案文本更匹配的领域 evidence chunk。
- 150 题正式评测必须在 10 题 smoke test 达标后再跑，避免浪费 A100。
