# MiniGeo

MiniGeo 是一个基于 Qwen3.5 的地学可信问答与数据分析 Agent 项目。项目目标不是训练新的基础模型，而是构建一个可评测的地学领域系统：包含 MiniGeo-Bench、RAG 检索增强生成、证据验证、QLoRA 微调准备，以及 SQL 支撑的数据分析 Agent 工作流。

## 当前状态

已在本地实现：

- `src/minigeo` 下的 Python 包结构。
- 150 条 UTF-8 中文 MiniGeo-Bench 种子评测集。
- 42 个稳定 `chunk_id` 的种子 RAG 语料 chunk。
- 中文可用 tokenizer：优先使用 `jieba`，无依赖时回退到字符和 bigram。
- 纯 Python BM25 检索器。
- 检索指标：`recall@k`、`MRR`、`citation_hit_rate`。
- 简单 Verifier 数据契约和启发式验证器。
- SQLite 演示数据库和 SQL 执行工具。
- 最小 Agent 报告接口。
- OpenAI-compatible Qwen 推理客户端。
- 基于模型服务的 RAG 生成链路。
- Dense retrieval / hybrid retrieval / reranker 的本地可测接口。
- 检索消融评测脚本。
- 面向 Colab Pro 的 QLoRA 配置占位。

尚未在本地完成：

- 真实 Qwen3.5 模型推理结果。
- Dense retrieval 和 reranker 推理。
- QLoRA 训练。
- 完整模型评测结果表。

这些阶段需要 Colab Pro、本机 GPU，或可访问的 OpenAI-compatible 模型服务。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:PYTHONPATH="src"
pytest -q
```

如果只运行标准库覆盖的部分，`pytest` 不需要安装完整模型依赖。

## 常用命令

```powershell
$env:PYTHONPATH="src"
python scripts/evaluate_bench.py
python scripts/expand_seed_data.py
python scripts/prepare_data.py
python scripts/evaluate_retrieval.py
python scripts/evaluate_retrieval_ablation.py
python scripts/rag_demo.py
python scripts/model_rag_demo.py
python scripts/evaluate_verifier.py
python scripts/sql_demo.py
python scripts/agent_demo.py
```

`scripts/model_rag_demo.py` 需要一个 OpenAI-compatible 的 Qwen 服务：

```powershell
$env:OPENAI_BASE_URL="http://localhost:8000/v1"
$env:OPENAI_API_KEY="EMPTY"
$env:MINIGEO_MODEL="Qwen/Qwen3.5-2B"
$env:PYTHONPATH="src"
python scripts/model_rag_demo.py
```

环境变量示例见 `configs/model_service.example.env`。

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

1. 将 MiniGeo-Bench 从 150 条扩展到 300+ 条。
2. 用更多可追踪公开地学资料增强当前种子 corpus。
3. 通过 OpenAI-compatible endpoint 跑通 Qwen3.5-2B 模型 RAG。
4. 将当前 hashing dense / lexical reranker 替换为 Qwen3-Embedding-0.6B 和 Qwen3-Reranker-0.6B。
5. 用模型增强 claim extraction 和 support classification。
6. 在 Colab Pro 上基于 `configs/qwen35_2b_lora.yaml` 运行 QLoRA SFT。
7. 扩展 SQL 评测和 MiniGeo-Agent。
8. 填充 `results/main_results.md` 和 `results/failure_cases.md`。

## 项目定位

MiniGeo 研究的是：轻量 Qwen3.5 系统能否通过领域 RAG、引用验证和 Agent 数据分析提高地学问答可靠性，而不是单纯依赖模型规模。
