# MiniGeo Qwen3.5 实施计划

> 面向后续 agentic worker：执行本计划时应优先保持测试驱动、可复现和小步提交。当前仓库已经完成本地 foundation、150 条种子 benchmark、BM25 RAG、OpenAI-compatible 模型接口、Verifier、SQL demo 和 Agent demo。

## 目标

构建一个基于 Qwen3.5 的地学可信问答与数据分析 Agent 系统。系统核心不是训练新的基础模型，而是建立可评测、可追踪、可拒答的领域应用闭环。

## 当前已完成

- Python 包结构：`src/minigeo`。
- Benchmark：`data/benchmark/minigeo_bench.jsonl`，150 条。
- RAG corpus：`data/processed/rag_corpus.jsonl`，42 个 chunk。
- 来源清单：`data/processed/source_manifest.jsonl`。
- 中文 tokenizer、BM25、检索指标。
- OpenAI-compatible Qwen 客户端。
- 模型 RAG 链路：`src/minigeo/rag/model_rag.py`。
- Dense retrieval / hybrid retrieval / reranker 本地接口。
- Embedding 服务客户端和 Reranker 服务客户端。
- 检索消融脚本：`scripts/evaluate_retrieval_ablation.py`。
- 分层 Verifier：claim extraction、evidence matching、support classification。
- Verifier 评测脚本：`scripts/evaluate_verifier.py`。
- SQLite demo SQL 工具。
- Agent 报告接口。
- QLoRA 配置：`configs/qwen35_2b_lora.yaml`。

## Task 1：保持本地基础测试绿灯

文件：

- `tests/`
- `src/minigeo/`

步骤：

```powershell
$env:PYTHONPATH="src"
python -m pytest -q
```

期望：

```text
20 passed
```

如果测试失败，先修复测试失败，再继续新增功能。

## Task 2：运行当前数据和检索评测

文件：

- `scripts/evaluate_bench.py`
- `scripts/prepare_data.py`
- `scripts/evaluate_retrieval.py`

步骤：

```powershell
$env:PYTHONPATH="src"
python scripts/evaluate_bench.py
python scripts/prepare_data.py
python scripts/evaluate_retrieval.py
```

当前参考结果：

```text
items=150
requires_sql=30
evidence_labeled=105
corpus_chunks=42
retrieval_recall@10=0.924
```

## Task 3：接入真实 Qwen3.5-2B 模型服务

文件：

- `configs/model_service.example.env`
- `scripts/model_rag_demo.py`
- `src/minigeo/llm/openai_compatible.py`
- `src/minigeo/rag/model_rag.py`

环境变量：

```powershell
$env:OPENAI_BASE_URL="http://localhost:8000/v1"
$env:OPENAI_API_KEY="EMPTY"
$env:MINIGEO_MODEL="Qwen/Qwen3.5-2B"
$env:PYTHONPATH="src"
```

运行：

```powershell
python scripts/model_rag_demo.py
```

期望：

- 输出 JSON-like 字典。
- 包含 `answer`、`citations`、`abstained`、`confidence`、`evidence`。
- citations 只包含本次检索得到的 chunk id。

## Task 4：扩展公开资料语料

文件：

- `data/processed/source_manifest.jsonl`
- `data/processed/rag_corpus.jsonl`
- `docs/data-card.md`

要求：

- 新增来源必须记录 URL、用途和 license 备注。
- 不提交版权不明确的原始文件。
- 新 chunk 必须有稳定 `chunk_id`。
- 新 benchmark evidence id 必须能在 corpus 中找到。

验证：

```powershell
$env:PYTHONPATH="src"
python -m pytest tests/test_seed_data.py -q
python scripts/evaluate_retrieval.py
```

## Task 5：替换为真实 dense retrieval 和 reranker

目标：

- 用 Qwen3-Embedding-0.6B 替换当前 hashing dense retriever。
- 用 Qwen3-Reranker-0.6B 或 bge-reranker 替换当前 lexical reranker。
- 对比 BM25、dense、hybrid、hybrid+reranker。

当前基础：

- `src/minigeo/rag/dense.py`
- `src/minigeo/rag/embedding_service.py`
- `src/minigeo/rag/hybrid.py`
- `src/minigeo/rag/reranker.py`
- `src/minigeo/rag/reranker_service.py`
- `scripts/evaluate_retrieval_ablation.py`

服务模式运行：

```powershell
$env:PYTHONPATH="src"
python scripts/evaluate_retrieval_ablation.py --use-services
```

指标：

- `retrieval_recall@5`
- `retrieval_recall@10`
- `MRR`
- `citation_hit_rate`
- `latency`

## Task 6：增强 Verifier

目标：

- 当前已经完成本地分层 Verifier。
- 下一步是用模型服务替换或增强 claim extraction 和 support classification。
- 继续记录 unsupported claim、contradicted claim 和 insufficient evidence。

当前基础：

- `src/minigeo/verifier/claim_extractor.py`
- `src/minigeo/verifier/evidence_matcher.py`
- `src/minigeo/verifier/verifier.py`
- `src/minigeo/verifier/support_classifier.py`
- `results/verifier_eval.md`

## Task 7：运行 QLoRA smoke test

文件：

- `configs/qwen35_2b_lora.yaml`
- `scripts/train_lora.py`

要求：

- 在 Colab Pro 或等价 GPU 环境执行。
- 先运行小样本 smoke test。
- 不直接用 MiniGeo-Bench reference answer 作为训练输出。

## Task 8：完善 SQL Agent

目标：

- 扩展 demo database。
- 实现 SQL 生成、执行、错误修复和结果验证。
- 将 SQL 结果和文档证据合并到最终报告。

现有基础：

- `src/minigeo/sql/tools.py`
- `scripts/sql_demo.py`
- `scripts/agent_demo.py`

## 完成标准

最终项目应能提供：

- MiniGeo-Bench 300+ 题。
- 可追踪 RAG corpus。
- Qwen3.5-2B RAG 真实模型结果。
- BM25 / dense / hybrid / reranker 消融表。
- Verifier 评测。
- SQL Agent demo。
- 主结果表和失败案例分析。
