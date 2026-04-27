# MiniGeo-Bench

## 目的

MiniGeo-Bench 是 MiniGeo 的评测基础。它用于衡量系统是否能：

- 基于证据回答地学问题。
- 在证据不足时拒答。
- 处理错误前提问题。
- 执行数据库支撑的分析任务。

## 当前种子评测集

当前文件：`data/benchmark/minigeo_bench.jsonl`。

- 总题数：300
- 可回答题：267
- 不可回答题：33
- 错误前提题：39
- SQL 支撑题：60
- 带 evidence label 的题：209

运行：

```powershell
$env:PYTHONPATH="src"
python scripts/evaluate_bench.py
python scripts/expand_seed_data.py --target-items 300
```

## 数据格式

每条题目是一行 JSON Lines 记录：

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

## 题型

| 类型 | 目的 |
|---|---|
| `concept` | 地学基础概念 |
| `mineral_property` | 矿物物理或化学性质 |
| `spectroscopy` | Raman、红外或其他光谱特征 |
| `evidence` | 需要引用文档证据的问题 |
| `multi_hop` | 需要多个证据 chunk 的问题 |
| `unanswerable` | 当前证据不足的问题 |
| `false_premise` | 问题包含错误前提 |
| `sql` | 需要结构化数据库查询的问题 |

## 标注规则

- 参考答案应简洁。
- 带证据题必须使用真实存在的 `chunk_id`。
- 当正确行为是拒答时，设置 `answerable=false`。
- SQL 题需要包含 `expected_sql_intent` 和 `expected_result`。
- 不要把 MiniGeo-Bench 的 reference answer 直接作为 SFT 输出训练。
- `scripts/expand_seed_data.py` 只用于确定性种子扩展；用于研究结论前必须人工复查新增题目。
- 当前 300 条 benchmark 是完整研究版的种子规模，后续应优先人工审查新增的 `unanswerable`、`false_premise`、`multi_hop` 和 `sql` 题。

## 指标

| 指标 | 定义 |
|---|---|
| `accuracy` | 最终回答是否匹配参考答案 |
| `citation_hit_rate` | 引用 chunk 是否覆盖 gold evidence |
| `unsupported_claim_rate` | 抽取 claim 中缺少证据支持的比例 |
| `abstention_accuracy` | 不可回答题是否触发拒答 |
| `sql_exec_accuracy` | SQL 是否执行成功并返回预期结果 |
| `latency` | 端到端响应时间 |
