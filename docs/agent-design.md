# MiniGeo-Agent 设计说明

## 目标

MiniGeo-Agent 用于回答同时需要结构化数据库分析和非结构化文档证据的问题。当前 demo 问题是：

```text
Analyze which mineral categories are most frequently misclassified in samples collected from Qinhuangdao, and explain possible causes using spectral evidence.
```

系统需要先用 SQL 找出秦皇岛样本中最常见的误判类别，再检索矿物和光谱证据，最后输出带验证报告的分析结果。

## 工具接口

| 工具 | 当前实现 | 输入 | 输出 |
|---|---|---|---|
| `search_docs` | `retrieve_with_bm25` | 查询文本、RAG corpus | top-k chunk |
| `retrieve_evidence` | `MiniGeoAgent._retrieve_evidence` | SQL 结果、corpus | 相关证据 chunk |
| `generate_sql` | `RuleBasedSQLGenerator.generate` / `ModelSQLGenerator` | 问题、schema | SQL |
| `execute_sql` | `execute_sql` | SQLite 路径、SQL | `execution_result` / `error` |
| `repair_sql` | `repair_sql` | SQL、错误信息 | 修复后的 SQL |
| `verify_answer` | `MiniGeoVerifier.verify` | answer、evidence | verifier report |
| `write_report` | `write_report` | answer、sql、evidence、verification、limitations | final report |

## 当前工作流

```text
question
-> generate_sql
-> execute_sql
-> retrieve_evidence
-> answer synthesis
-> verify_answer
-> write_report
```

当前 demo 的 SQL 会按 `predicted_mineral` 汇总秦皇岛误判样本：

```sql
select predictions.predicted_mineral, count(*) as errors
from predictions
join samples on samples.sample_id = predictions.sample_id
where samples.region = 'Qinhuangdao' and predictions.is_correct = 0
group by predicted_mineral
order by errors desc
```

本地演示数据库返回：

```text
feldspar: 2
quartz: 1
```

证据链包含两类证据：

- SQL 结果证据：`agent_sql#result`，用于支持“秦皇岛样本最常被误判为 feldspar，误判分布为 feldspar 2 次、quartz 1 次”这类统计 claim。
- 文档证据：优先保留与预测矿物类别相关的 chunk，例如 `doc_feldspar#chunk_002` 和 `doc_quartz#chunk_002`。

## 输出契约

Agent final report 必须包含：

```json
{
  "answer": "...",
  "sql": "...",
  "sql_result": {
    "sql": "...",
    "execution_result": [],
    "error": null
  },
  "evidence": ["agent_sql#result", "doc_feldspar#chunk_002"],
  "verification": {
    "verdict": "supported|partially_supported|unsupported|contradicted|insufficient_evidence",
    "claims": []
  },
  "limitations": []
}
```

## 评测口径

当前本地评测包含：

- `sql_exec_accuracy`：SQL 执行结果是否匹配 benchmark 的 `expected_result`。
- `citation_hit_rate`：检索结果是否命中 evidence label。
- `unsupported_claim_rate`：Verifier 中非 supported claim 占比。
- `abstention_accuracy`：系统对 answerable / unanswerable 题的拒答行为是否正确。
- `latency_ms`：平均每题或每次 demo 的本地耗时。

一键验收命令：

```powershell
python scripts/audit_project.py
```

## 当前限制

- 当前 Agent 是确定性 MVP，不包含完整 planner。
- SQL generator 默认是规则型 baseline；模型模式需要 OpenAI-compatible Qwen 服务。
- demo database 很小，结果只用于验证工具链。
- 当前 SQL 结果已被转换为 `agent_sql#result` 证据，能支持 SQL 统计类 claim；但它仍是 demo database 的执行结果，不等同于真实实验结论。
- 文档证据仍是种子 corpus，后续需要更多公开资料和人工 evidence label。

## 下一步

1. 增加 planner：判断问题是否需要文档检索、SQL 或二者混合。
2. 将 SQL 结果也转换成 verifier 可检查的 evidence。
3. 加入模型 SQL generator 与规则 baseline 对比。
4. 扩展 Agent benchmark，单独记录 final answer quality。
