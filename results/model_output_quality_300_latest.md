# MiniGeo 模型输出质量审计

本报告基于已保存的模型服务 JSONL 输出离线生成，不会再次调用模型。

| Mode | Items | Citation Miss | Thinking Answer | Placeholder Answer | Format Error | Abstention Error | Request Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| rag | 300 | 0.217 | 0.000 | 0.000 | 0.000 | 0.237 | 0 |
| no-rag | 300 | 0.697 | 0.000 | 0.000 | 0.000 | 0.217 | 0 |

## 解释

- `Citation Miss`：answerable/evidence 题中，模型 citation 未命中 benchmark evidence。
- `Thinking Answer`：最终 `answer` 字段仍包含 Thinking Process，说明输出格式未完全受控。
- `Placeholder Answer`：模型输出了空答案或 `string` 这类 schema 占位文本。
- `Format Error`：parser 明确判定该输出不满足最终 JSON contract。
- `Abstention Error`：模型拒答行为与 benchmark 的 `answerable` 标签不一致。
