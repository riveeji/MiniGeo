# MiniGeo SQL 评测

当前评测使用规则型 SQL 生成器、SQLite 演示数据库和 SQL 修复函数，对 `data/benchmark/minigeo_bench.jsonl` 中 `requires_sql=true` 的题目进行评测。

运行：

```powershell
python scripts/evaluate_sql.py
```

当前结果：

```text
sql_items=30
sql_exec_accuracy=1.0
failures={}
```

说明：

- 当前结果基于演示数据库和规则型 SQL generator。
- 已支持 `python scripts/evaluate_sql.py --use-model` 接入模型 SQL generator。
- 后续应运行模型 SQL generator，并与规则型 baseline 做对比。
- 对于 `expected_result` 中的 `table` / `tables`，评测会同时检查 SQL 文本和执行结果。
