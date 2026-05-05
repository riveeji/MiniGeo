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
-> plan_agent_tools
-> generate_sql
-> execute_sql
-> retrieve_evidence
-> answer synthesis
-> verify_answer
-> write_report
```

当前 demo 的 SQL 会按 `predicted_mineral` 汇总秦皇岛误判样本：

`plan_agent_tools` 会把该问题路由为 `mode=hybrid`，并选择 `generate_sql`、`execute_sql`、`retrieve_evidence`、`verify_answer` 和 `write_report`。

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
- Agent 多案例回归：固定覆盖 `hybrid`、`sql`、`docs` 三类路由，检查 final report 是否包含 answer、SQL、evidence、verification 和 limitations。
- `latency_ms`：平均每题或每次 demo 的本地耗时。

一键验收命令：

```powershell
python scripts/audit_project.py
```

单独运行 Agent 多案例评测：

```powershell
python scripts/evaluate_agent_cases.py
```

输出写入：

- `results/agent_cases.json`
- `results/agent_cases.md`

## 当前限制

- 当前 Agent 是确定性 MVP，planner 仍是规则型 baseline。
- SQL generator 默认是规则型 baseline；模型模式需要 OpenAI-compatible Qwen 服务。
- demo database 很小，结果只用于验证工具链。
- 当前 SQL 结果已被转换为 `agent_sql#result` 证据，能支持 SQL 统计类 claim；但它仍是 demo database 的执行结果，不等同于真实实验结论。
- 文档证据仍是种子 corpus，后续需要更多公开资料和人工 evidence label。

## 下一步

1. 扩展 Agent benchmark，加入更多真实混合问题并单独记录 final answer quality。
2. 把规则 planner 替换或增强为模型 planner，但保留当前规则 baseline 作为回归对照。
3. 扩展模型 SQL generator 题集，目前 60 条 SQL 题上 Qwen3.5-4B 与规则 baseline 均为 `sql_exec_accuracy=1.0`。
4. 在真实 SFT 模型完成后，对比 base Agent 与 SFT Agent。
