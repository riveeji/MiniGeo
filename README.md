# MiniGeo

MiniGeo 是一个基于 Qwen3.5 的地学可信问答与数据分析 Agent 项目。项目目标不是训练新的基础模型，而是构建一个可评测的地学领域系统：包含 MiniGeo-Bench、RAG 检索增强生成、证据验证、QLoRA 微调准备，以及 SQL 支撑的数据分析 Agent 工作流。

## 当前状态

本地已经实现：

- `src/minigeo` 下的 Python 包结构。
- 300 条 UTF-8 中文 MiniGeo-Bench 种子评测集。
- 42 个稳定 `chunk_id` 的种子 RAG 语料 chunk，非 system chunk 已绑定真实公开来源 URL。
- 中文可用 tokenizer：优先使用 `jieba`，无依赖时回退到字符和 bigram。
- 纯 Python BM25 检索器。
- 检索指标：`recall@k`、`MRR`、`citation_hit_rate`。
- OpenAI-compatible Qwen 推理客户端。
- 基于模型服务的 RAG 生成链路。
- RAG citation 约束与轻量后处理：要求 citation 直接支撑答案，并修正非系统问题中明显泛化的 `doc_system` 引用。
- RAG + Verifier 离线后处理：对已保存模型输出执行 claim verification，并在证据不足时保守拒答。
- Verifier 拦截样例导出：把被改写为拒答的模型答案导出为 CSV/Markdown，辅助检查误杀。
- Qwen3.5-4B 模型服务小规模 RAG/no-RAG 对照结果。
- 模型输出质量审计：citation miss、thinking 泄漏、占位答案、拒答错误。
- 模型 citation miss 失败归因：区分检索未召回、模型拒答、相邻 chunk 引用和错误引用。
- citation miss 人工抽检导出：生成 CSV/Markdown，辅助判断模型错误或 evidence label 需扩充。
- Dense retrieval、hybrid retrieval、reranker 的本地可测接口。
- OpenAI-compatible embedding 服务客户端和 `/rerank` 服务客户端。
- 真实 `Qwen/Qwen3-Embedding-0.6B` staged 服务消融：已在 Colab A100 + vLLM + Cloudflare tunnel 上跑通 `--use-embedding-service`。
- 分层 Verifier：claim 抽取、证据匹配、支持性分类。
- Verifier 评测统计：verdict/status 分布和 unsupported claim rate。
- SQLite 演示数据库、SQL 生成、SQL 修复和 execution accuracy 评测。
- 最小 Agent 报告接口。
- MiniGeo-Agent 多案例本地评测：覆盖 `hybrid`、`sql`、`docs` 三类路由，输出 answer、SQL、evidence、verification 和 limitations 回归报告。
- Colab A100 上已生成 `MiniGeo-Qwen3.5-2B-SFT-128step` LoRA adapter，artifact 检查见 `results/qlora_128step.md`。
- SFT 草案数据构建脚本，带 benchmark reference answer 泄漏检查。
- SFT corpus 已改为 JSON-only 输出合同：`answer/citations/abstained/confidence`，并显式避免 `<think>` 标签和多 JSON 串联。
- 数据质量审计已检查 evidence 断链、SFT 泄漏、重复 ID、metadata 缺失和非 system corpus 占位 URL。
- 面向 Colab Pro 的 QLoRA 配置占位。

本地阶段当前已经收口到可交付状态：

- 本地 Git 工作区已清理，正常只保留 `.venv/` 和 `checkpoints/qlora-smoke/` 两类 ignored 本地产物。
- `MiniGeo-Qwen3.5-2B-SFT-128step` adapter 已通过 artifact 检查和真实 smoke10 推理检查。
- SFT smoke10 已完成离线重解析：`citation_hit_rate=0.444`，`abstention_accuracy=1.000`，但 raw output 仍有 `</think>` 和多 JSON 串联问题。
- `Qwen/Qwen3.5-2B` base 同题 smoke10 已完成：`citation_hit_rate=0.000`，`abstention_accuracy=0.900`。
- 128step SFT 相比 base 改善 citation/refusal 指标，但 thinking 泄漏更严重：base 为 1/10，SFT 为 7/10。
- SFT 输出模板、训练样本格式和 generation prompt 已本地修订；json64 A100 短训把 `thinking_raw_outputs` 降到 0/10，但 `citation_hit_rate=0.000`、`abstention_accuracy=0.100`，不能继续长训。
- SFT adapter smoke 已改为对 evidence-labeled 题目注入 gold evidence block；下一步上传 json64 zip 复评 citation behavior，不需要重训。

尚未完成：

- 真实检索服务的 cold/warm latency 专项评测。
- 使用 evidence-conditioned smoke 重新评估 JSON-only SFT。当前 128step adapter 和 json64 adapter 已生成，1 epoch adapter 仍未生成。
- QLoRA/SFT 后的完整 benchmark 主结果表。

这些阶段需要 Colab Pro、本机 GPU，或可访问的 OpenAI-compatible 模型服务。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

本地开发和单元测试只需要 `requirements-dev.txt`。它会以 editable 模式安装当前项目，因此运行脚本时不需要手动设置 `PYTHONPATH`。

`requirements.txt` / `requirements-model.txt` 包含 torch、transformers、gradio、Pillow 等重型模型依赖，建议在 Python 3.10-3.12 或 Colab Pro 中安装，不建议在 Windows + Python 3.14 上一次性安装。

## 一键验收

```powershell
python scripts/audit_project.py
```

该命令会依次运行单元测试、benchmark 分布统计、检索消融、Verifier 评测、SQL 评测、Agent 多案例评测、SFT 数据构建和本地结果摘要，并写入 `results/local_audit.md`。

Colab Pro 模板见 `notebooks/minigeo_colab_template.ipynb`，用于模型服务评测、SFT 数据构建和 QLoRA 配置检查。下一轮 base/SFT 对照的完整顺序执行 cells 见 `docs/a100-sft-base-cells.md`。

Agent 设计说明见 `docs/agent-design.md`。
展示版总览见 `docs/project-showcase.md`。

模型服务评测执行说明见 `docs/model-eval-runbook.md`。下次开启 A100 时，先跑 10 题 smoke test，通过后再跑 150 或 300 题正式评测。

## 常用命令

```powershell
python scripts/evaluate_bench.py
python scripts/expand_seed_data.py --target-items 300
python scripts/prepare_data.py
python scripts/evaluate_retrieval.py
python scripts/evaluate_retrieval_ablation.py
python scripts/analyze_retrieval_failures.py
python scripts/evaluate_abstention.py
python scripts/rag_demo.py
python scripts/model_rag_demo.py
python scripts/evaluate_model_service.py --limit 3 --selection evidence
python scripts/evaluate_model_service.py --limit 300 --selection all --mode both --dry-run
python scripts/evaluate_base_model.py --dry-run
python scripts/audit_model_outputs.py
python scripts/analyze_model_failures.py
python scripts/export_failure_review.py
python scripts/evaluate_verified_model_service.py
python scripts/export_verifier_interceptions.py
python scripts/evaluate_verifier.py
python scripts/evaluate_sql.py
python scripts/evaluate_agent_planner.py
python scripts/evaluate_agent_cases.py
python scripts/write_local_results.py
python scripts/build_sft_corpus.py
python scripts/audit_data_quality.py
python scripts/train_lora.py --check-only
python scripts/run_qlora_smoke.py --dry-run
python scripts/evaluate_sft_adapter.py --adapter-dir checkpoints/MiniGeo-Qwen3.5-2B-SFT-128step/adapter --dry-run
python scripts/reparse_sft_adapter_outputs.py
python scripts/write_report_artifacts.py
python scripts/sql_demo.py
python scripts/agent_demo.py
```

`scripts/model_rag_demo.py` 需要一个 OpenAI-compatible 的 Qwen 服务：

```powershell
$env:OPENAI_BASE_URL="http://localhost:8000/v1"
$env:OPENAI_API_KEY="EMPTY"
$env:MINIGEO_MODEL="Qwen/Qwen3.5-2B"
python scripts/model_rag_demo.py
```

环境变量示例见 `configs/model_service.example.env`。

如果已经保存了模型服务输出，可以离线审计输出质量：

```powershell
python scripts/audit_model_outputs.py
python scripts/analyze_model_failures.py
python scripts/export_failure_review.py
python scripts/evaluate_verified_model_service.py
python scripts/export_verifier_interceptions.py
```

报告写入 `results/model_output_quality_150.md`、`results/model_failure_analysis_150.md`、`results/model_failure_review_150.*`、`results/model_service_verified_eval_150.md` 和 `results/verifier_interceptions_150.*`，不需要 GPU，也不会再次调用模型。

如果要用真实 embedding/reranker 服务运行消融评测：

```powershell
$env:MINIGEO_EMBEDDING_BASE_URL="http://localhost:8000/v1"
$env:MINIGEO_EMBEDDING_API_KEY="EMPTY"
$env:MINIGEO_EMBEDDING_MODEL="Qwen/Qwen3-Embedding-0.6B"
$env:MINIGEO_RERANKER_BASE_URL="http://localhost:8000/v1"
$env:MINIGEO_RERANKER_API_KEY="EMPTY"
$env:MINIGEO_RERANKER_MODEL="Qwen/Qwen3-Reranker-0.6B"
python scripts/evaluate_retrieval_ablation.py --use-services
```

默认不加 `--use-services` 时，脚本使用本地 deterministic baseline，方便无模型服务时做回归测试。单 A100 不能同时跑 embedding 与 reranker 服务时，可以分阶段运行：

```powershell
python scripts/evaluate_retrieval_ablation.py --use-embedding-service --json-output results/retrieval_service_eval.json --markdown-output results/retrieval_service_eval.md
python scripts/evaluate_retrieval_ablation.py --use-reranker-service --json-output results/retrieval_service_eval.json --markdown-output results/retrieval_service_eval.md
```

当前已保存的真实检索服务结果见 `results/retrieval_service_eval.md`。在 42 条 seed corpus 上，`Qwen3-Embedding dense` 的 `citation_hit_rate=0.957`，`BM25 + Qwen3-Embedding hybrid` 的 `citation_hit_rate=1.000`；本地 lexical reranker 会把结果拉低到 `0.900`，而真实 `Qwen/Qwen3-Reranker-0.6B` staged run 把 hybrid rerank 提升到 `0.995`。

如果要启用模型辅助 Verifier：

```powershell
$env:MINIGEO_VERIFIER_BASE_URL="http://localhost:8000/v1"
$env:MINIGEO_VERIFIER_API_KEY="EMPTY"
$env:MINIGEO_VERIFIER_MODEL="Qwen/Qwen3.5-2B"
python scripts/evaluate_verifier.py --use-model
```

如果要启用模型 SQL generator：

```powershell
$env:MINIGEO_SQL_BASE_URL="http://localhost:8000/v1"
$env:MINIGEO_SQL_API_KEY="EMPTY"
$env:MINIGEO_SQL_MODEL="Qwen/Qwen3.5-2B"
python scripts/evaluate_sql.py --use-model
```

如果要在 Colab A100 上加载 128step SFT adapter 做推理 smoke test，并同时跑 `Qwen/Qwen3.5-2B` base 对照，见 `docs/sft-adapter-eval-runbook.md`。当前 `minigeo_sft_adapter_eval_128step (1).zip` 已包含真实 SFT smoke10 结果；记录见 `results/sft_adapter_eval_128step.md`。如果只想离线重解析已有 raw output，运行 `python scripts/reparse_sft_adapter_outputs.py`。

## 核心接口

Benchmark 条目：

```json
{
  "id": "minigeo_001",
  "question": "石英的主要化学成分是什么？",
  "answer": "石英的主要化学成分是二氧化硅。",
  "type": "concept",
  "difficulty": "easy",
  "answerable": true,
  "requires_sql": false,
  "evidence": ["doc_quartz#chunk_001"],
  "expected_sql_intent": null,
  "expected_result": null
}
```

RAG 回答：

```json
{
  "answer": "根据证据生成的回答。",
  "citations": ["doc_quartz#chunk_001"],
  "abstained": false,
  "confidence": 0.7
}
```

Verifier 报告：

```json
{
  "verdict": "supported",
  "claims": [
    {
      "claim": "石英的主要成分是二氧化硅。",
      "status": "supported",
      "evidence": ["doc_quartz#chunk_001"],
      "confidence": 0.8
    }
  ]
}
```

## 路线图

本地不依赖 A100 的验收、检索失败分析和展示文档已经收敛；真实 embedding/reranker staged 服务消融、QLoRA smoke run、128step adapter artifact 和 128step adapter smoke10 也已完成。下一批仍需放到 A100 或 GPU 环境上执行：

1. 修正 SFT adapter smoke prompt，把 gold evidence block 放入 evidence-labeled 题目。
2. 用 evidence-conditioned smoke 复测 json64 adapter 的 citation behavior。
3. 若 citation/refusal 和输出格式同时改善，再决定是否继续运行 553step 或 1 epoch SFT。

## 项目定位

MiniGeo 研究的是：轻量 Qwen3.5 系统能否通过领域 RAG、引用验证和 Agent 数据分析提高地学问答可靠性，而不是单纯依赖模型规模。
