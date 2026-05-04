# MiniGeo Data Card

## 目的

本文档记录 MiniGeo 的数据来源、处理规则和已知风险。每次新增原始文档、benchmark 题目、RAG chunk 或 SFT 样本后，都应更新本文件。

## 当前数据资产

| 文件 | 用途 |
|---|---|
| `data/benchmark/minigeo_bench.jsonl` | 300 条 MiniGeo-Bench 种子评测集 |
| `data/processed/rag_corpus.jsonl` | 42 个本地 RAG 测试用证据 chunk |
| `data/processed/source_manifest.jsonl` | 28 条公开来源 URL、用途和 license 备注 |
| `data/processed/sft_corpus.jsonl` | 553 条 SFT 草案样本 |
| `data/processed/minigeo_demo.sqlite` | 由 `scripts/init_demo_db.py` 生成的演示数据库，属于运行产物，不提交 |

当前 corpus 是用于管线验证的种子语料。非 system chunk 已替换为可追踪公开来源 URL，正文仍是人工整理的短证据摘要，不提交未确认再分发权限的原文。报告最终研究结论前，仍应继续扩展更多公开资料，并人工复核来源和内容对应关系。

## RAG Corpus Schema

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

## SFT Corpus Schema

```json
{
  "id": "sft_0001",
  "instruction": "根据证据回答问题；如果证据不足，应明确拒答。",
  "input": "Question and evidence.",
  "output": "Grounded answer with citations.",
  "task_type": "evidence_qa"
}
```

## SFT 样本策略

当前 `scripts/build_sft_corpus.py` 生成 553 条草案样本：

- `evidence_summary`：基于 RAG chunk 生成引用格式训练样本。
- `evidence_qa`：基于 benchmark question 和对应 evidence chunk 生成带 citation 的简短证据回答。
- `verification_rewrite`：基于不可靠回答和 evidence chunk 生成受证据约束的保守改写。
- `refusal`：基于不可回答 benchmark 问题生成通用拒答样本。
- `sql_format`：基于 SQL benchmark 生成 SQL intent 格式样本。

当前 task_type 分布：

| task_type | samples |
|---|---:|
| `evidence_summary` | 42 |
| `evidence_qa` | 209 |
| `verification_rewrite` | 209 |
| `refusal` | 33 |
| `sql_format` | 60 |

泄漏控制：

- 不直接复制 MiniGeo-Bench reference answer 作为 SFT 输出。
- 运行 `find_reference_answer_leaks` 检查 exact output copy。
- 当前生成结果：`reference_answer_leaks=[]`。

## 处理流程

```text
公开来源元数据
-> 解析或人工整理
-> 清洗 UTF-8 文本
-> 删除空 chunk 和重复 chunk
-> 分配稳定 chunk id
-> 添加 source、url、topic、mineral、license
-> 导出 JSONL
-> 运行 corpus 校验、检索评测和泄漏检查
```

## 数据质量检查

- 所有文本文件使用 UTF-8。
- 删除完全重复的 chunk。
- 删除空 chunk 或过短 chunk。
- 尽量记录来源 URL 和 license。
- 非 system chunk 不允许使用 `example.org/minigeo` 占位 URL；`scripts/audit_data_quality.py` 会把它列为失败项。
- Benchmark reference answer 不进入 SFT 输出。
- 每次更新后记录 corpus 规模、topic 分布和 SFT 样本数。

## 泄漏控制

- 不直接用 MiniGeo-Bench reference answer 训练。
- Open-book RAG 评测可以访问 evidence chunk，但不能把答案文本复用为训练输出。
- 明确区分 closed-book generation、open-book RAG 和 SFT evaluation。

## 版权说明

- 可以提交公开元数据和处理脚本。
- 不提交再分发权限不明确的原始文件。
- 每个非人工整理来源都应记录 source name、URL、license 和再分发状态。
