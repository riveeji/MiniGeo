# MiniGeo 路线图

## 目标

构建一个基于 Qwen3.5 的地学可信问答与数据分析系统。最终系统应结合 RAG、证据验证、LoRA/QLoRA 微调、benchmark 评测，以及 SQL 支撑的 Agent 分析层。

## 指导原则

MiniGeo 不以模型规模作为主要竞争点，而以以下能力作为核心贡献：

- 高质量领域 benchmark。
- 基于证据的回答生成。
- 证据不足时的拒答行为。
- 非结构化文档和结构化数据库的结合。
- 清晰的评测和消融结果。

## Phase 0：项目基础

周期：1 天。

产出：

- Git 仓库。
- Python 环境。
- 基本目录结构。
- README 和 docs。
- Colab notebook 模板。

推荐依赖：

```text
torch
transformers
peft
bitsandbytes
datasets
accelerate
sentence-transformers
faiss-cpu
rank-bm25
jieba
pandas
numpy
scikit-learn
tqdm
pyyaml
fastapi
uvicorn
gradio
pytest
openai
```

## Phase 1：MiniGeo-Bench

周期：3-5 天。

目的：先建立评测基础，再实现复杂模型链路。

规模目标：

- MVP：50 题。
- 简历可展示版：150-300 题。
- 强版本：300+ 题，并尽量带 evidence label。

题型：

| 类型 | 说明 |
|---|---|
| `concept` | 地学基础概念 |
| `mineral_property` | 矿物物理和化学性质 |
| `spectroscopy` | Raman、红外或其他光谱特征 |
| `evidence` | 需要文档引用的问题 |
| `multi_hop` | 需要多个证据 chunk 的问题 |
| `unanswerable` | 当前证据不足的问题 |
| `false_premise` | 问题包含错误前提 |
| `sql` | 需要结构化数据库查询的问题 |

当前产出：

- `data/benchmark/minigeo_bench.jsonl`
- `docs/benchmark.md`
- `scripts/evaluate_bench.py`

## Phase 2：数据管线

周期：4-7 天。

目的：把公开地学资料转为 RAG chunk 和 SFT 样本。

流程：

```text
公开资料
-> 解析
-> 清洗
-> 去重
-> chunk
-> 元数据标注
-> train / validation / test 切分
-> RAG corpus 和 SFT corpus
```

产出：

- `scripts/prepare_data.py`
- `data/processed/rag_corpus.jsonl`
- `data/processed/sft_corpus.jsonl`
- `docs/data-card.md`

## Phase 3：Qwen3.5-2B RAG MVP

周期：5-7 天。

目的：在微调前先做出可用系统。

流程：

```text
question
-> BM25 retrieval
-> evidence prompt construction
-> Qwen3.5-2B generation
-> JSON answer parsing
-> citation filtering
-> cited answer
```

后续增强：

```text
BM25 retrieval
-> embedding retrieval
-> hybrid merge
-> rerank
```

当前本地检索状态：

```text
benchmark_items=300
evidence_labeled=209
BM25 + query expansion citation_hit@10=1.000
Hybrid RAG baseline citation_hit@10=0.995
```

说明：该结果基于确定性种子 benchmark 和领域 query expansion。用于正式研究结论前，应继续扩展公开资料和人工复核 failure cases，避免只对当前 gold evidence 过拟合。

当前产出：

- `src/minigeo/rag/bm25.py`
- `src/minigeo/rag/dense.py`
- `src/minigeo/rag/embedding_service.py`
- `src/minigeo/rag/hybrid.py`
- `src/minigeo/rag/reranker.py`
- `src/minigeo/rag/reranker_service.py`
- `src/minigeo/rag/pipeline.py`
- `src/minigeo/rag/model_rag.py`
- `src/minigeo/rag/verified_model_rag.py`
- `src/minigeo/llm/openai_compatible.py`
- `scripts/rag_demo.py`
- `scripts/model_rag_demo.py`
- `scripts/evaluate_retrieval_ablation.py`
- `scripts/evaluate_verified_model_service.py`

成功标准：

- demo 能回答 benchmark 中至少 20 个问题。
- 每个回答包含 source chunk id。
- RAG 的 citation hit rate 高于 no-RAG。
- BM25、dense、hybrid、hybrid+rerank 可以在同一 benchmark 上做消融评测。
- 加 `--use-services` 后可以接入真实 embedding 和 reranker 服务。

## Phase 4：MiniGeo-Verifier

周期：5-7 天。

目的：通过证据支持性检查，让 MiniGeo 区别于普通 RAG。

流程：

```text
answer
-> claim extraction
-> evidence matching
-> support classification
-> rewrite or abstain
```

标签：

- `supported`
- `contradicted`
- `insufficient`

产出：

- `src/minigeo/verifier/`
- `scripts/evaluate_verifier.py`
- `results/verifier_eval.md`

成功标准：

- Unsupported claim rate 可测。
- unanswerable 问题触发拒答。
- Verifier 能说明每个 claim 的支持证据或证据不足原因。

当前本地启发式评测结果：

```text
Qwen3.5-4B + BM25 RAG + Verifier，150 题离线后处理
reports=150
supported=104
skipped=44
insufficient_evidence=2
unsupported_claim_rate=0.017
```

该结果基于已保存的模型 RAG 输出和本地 heuristic Verifier。剩余拦截样例见 `results/verifier_interceptions_150.md`，后续可用模型辅助 Verifier 复判。

模型辅助模式：

```powershell
python scripts/evaluate_verifier.py --use-model
```

## Phase 5：Qwen3.5-2B LoRA / QLoRA

周期：7-10 天。

目的：训练 `MiniGeo-Qwen3.5-2B-SFT`，但不让微调成为项目成败单点。

训练数据：

- 地学问答。
- 基于证据的回答。
- 拒答样本。
- SQL 格式样本。
- 少量 reasoning distillation 样本。

策略：

- 先使用 QLoRA。
- 默认 LoRA rank 16。
- 先跑小样本 smoke run，再完整训练。

产出：

- `configs/qwen35_2b_lora.yaml`
- `scripts/train_lora.py`
- `src/minigeo/finetune/`
- `results/sft_eval.md`

## Phase 6：Qwen3.5-4B 强基线

周期：3-5 天。

目的：比较“小模型 + RAG + Verifier”是否能在可靠性指标上接近或超过更大的无 RAG 基线。

评测组：

- Qwen3.5-2B。
- Qwen3.5-2B + RAG。
- MiniGeo-Qwen3.5-2B-SFT + RAG。
- MiniGeo-Qwen3.5-2B-SFT + RAG + Verifier。
- Qwen3.5-4B。
- Qwen3.5-4B + RAG。

产出：

- `results/main_results.md`

## Phase 7：MiniGeo-Agent

周期：7-14 天。

目的：从可信 QA 升级为数据分析 Agent。

工具：

| 工具 | 用途 |
|---|---|
| `search_docs` | 搜索地学文档 |
| `retrieve_evidence` | 返回证据 chunk |
| `generate_sql` | 从自然语言生成 SQL |
| `execute_sql` | 执行 SQL |
| `repair_sql` | 根据错误信息和 schema 修复 SQL |
| `verify_answer` | 检查最终回答证据支持性 |
| `write_report` | 生成证据支持的分析报告 |

产出：

- `src/minigeo/agent/`
- `src/minigeo/sql/generator.py`
- `src/minigeo/sql/model_generator.py`
- `src/minigeo/sql/repair.py`
- `src/minigeo/eval/sql.py`
- `scripts/init_demo_db.py`
- `scripts/evaluate_sql.py`
- `scripts/agent_demo.py`
- `docs/agent-design.md`

当前规则型 SQL baseline：

```text
sql_items=30
sql_exec_accuracy=1.0
```

已支持 `python scripts/evaluate_sql.py --use-model` 接入模型 SQL generator。后续应运行模型 SQL generator，并与规则型 baseline 对比。

## Phase 8：可选 MiniGeo-Tiny

周期：7-10 天。

目的：展示对 LLM 训练链条的理解，不作为主贡献。

可包含：

- Tokenizer 训练。
- Decoder-only Transformer。
- RoPE。
- RMSNorm。
- SwiGLU。
- KV cache。
- Pretraining。
- SFT。

## Phase 9：打包展示

周期：3-5 天。

最终产物：

- README。
- 架构图。
- MiniGeo-Bench 文档。
- Data card。
- 主结果表。
- 失败案例分析。
- Colab notebook。
- 简历 bullet。

推荐简历表述：

> MiniGeo：构建基于 Qwen3.5 的地学可信问答与数据分析 Agent 系统，包含领域 benchmark 构建、混合 RAG、引用验证、LoRA 微调和 Text-to-SQL Agent 工作流。

## 当前 A100 前置状态

本地可执行的前置工作已经完成到以下状态：

- MiniGeo-Bench 已扩展到 300 条。
- BM25、dense/hybrid/reranker 本地 deterministic 消融接口已实现。
- Qwen3.5-4B 的 300 题 RAG/no-RAG 已保存，并完成输出质量审计、citation miss 归因、人工抽检导出。
- RAG + Verifier 的 300 题离线后处理已接入主结果表。
- Verifier 拦截样例已导出，当前 300 题剩余 5 条拦截样例。

下一批必须依赖 A100 或外部模型服务的任务：

1. 运行真实 Qwen3-Embedding-0.6B / Qwen3-Reranker-0.6B 服务消融。
2. 运行模型辅助 Verifier，复判 `results/verifier_interceptions_300_latest.md`。
3. 运行 QLoRA smoke run。
