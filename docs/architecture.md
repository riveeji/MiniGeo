# MiniGeo 架构

## 系统总览

MiniGeo 按分层系统组织：

```text
用户问题
  |
  v
任务路由 / Agent 规划
  |
  +--> 文档 RAG
  |      +--> Chunk 索引
  |      +--> BM25 检索
  |      +--> Embedding 检索
  |      +--> Reranker 重排
  |
  +--> SQL 工具
  |      +--> Schema 读取
  |      +--> SQL 生成
  |      +--> SQL 执行
  |      +--> SQL 修复
  |
  +--> Qwen3.5 生成器
  |
  +--> 引用验证器
         +--> Claim 抽取
         +--> 证据匹配
         +--> 支持性分类
         +--> 改写或拒答
```

## 模型层

默认模型角色：

- 主生成模型：Qwen3.5-2B。
- 轻量基线：Qwen3.5-0.8B。
- 强基线：Qwen3.5-4B。
- 教师模型：Qwen3.5-27B 或 Qwen3.5-35B-A3B。

模型职责：

- 理解地学问题。
- 基于证据生成回答。
- 在需要时生成 SQL。
- 输出简短推理或结构化结果。
- 在 Agent 层支持工具调用格式。

## RAG 层

RAG 为系统提供外部地学知识。

核心组件：

- 文档解析。
- Chunk 切分。
- 元数据存储。
- BM25 检索。
- Embedding 检索。
- Reranker 重排。
- Prompt 组装。

Chunk schema：

```json
{
  "chunk_id": "doc_quartz#chunk_001",
  "doc_id": "doc_quartz",
  "text": "石英是常见的硅酸盐矿物，主要化学成分是二氧化硅 SiO2。",
  "source": "PubChem Quartz",
  "url": "https://pubchem.ncbi.nlm.nih.gov/compound/Quartz",
  "page": null,
  "topic": "concept",
  "mineral": "quartz",
  "license": "source_metadata_only"
}
```

## Verifier 层

Verifier 检查生成回答中的事实 claim 是否被检索证据支持。

输入：

- 用户问题。
- 生成回答。
- 检索到的证据 chunk。

输出：

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

当前实现已经拆分为三层：

- `claim_extractor.py`：本地句子切分和模型辅助 claim 抽取。
- `evidence_matcher.py`：按 token overlap 找最相关证据 chunk。
- `support_classifier.py`：启发式或模型辅助支持性分类。
- `verifier.py`：组装完整验证报告。

标签：

- `supported`
- `partially_supported`
- `unsupported`
- `contradicted`
- `insufficient_evidence`

## Agent 层

Agent 负责判断问题是否需要文档检索、SQL 查询、证据验证或报告生成。

| 工具 | 输入 | 输出 |
|---|---|---|
| `search_docs` | 问题 | 证据 chunk |
| `generate_sql` | 问题和 schema | SQL 查询 |
| `execute_sql` | SQL 查询 | 表格结果 |
| `repair_sql` | SQL 和错误信息 | 修复后的 SQL |
| `verify_answer` | 回答和证据 | 验证报告 |
| `write_report` | 验证后的结果 | 最终报告 |

示例工作流：

```text
问题：秦皇岛样本中哪些矿物类别最常被误判，可能原因是什么？

1. 读取数据库 schema。
2. 生成 SQL 查找误判类别。
3. 执行 SQL。
4. 根据误判类别检索矿物性质和光谱文档。
5. 生成带引用的解释。
6. 验证 claim 是否被证据支持。
7. 返回回答、SQL、证据和验证报告。
```

## 评测层

MiniGeo 必须评测语言质量和系统可靠性。

核心指标：

- 答案准确率。
- Citation hit rate。
- Unsupported claim rate。
- Hallucination rate。
- Abstention accuracy。
- SQL execution accuracy。
- SQL repair success rate。
- Latency。
