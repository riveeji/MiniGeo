# MiniGeo 主结果

本表由 `scripts/write_report_artifacts.py` 生成。当前数值是本地 baseline 和 demo 结果，不代表真实 Qwen3.5 模型服务或 QLoRA 训练结果。

| System | Acc | Citation Hit | Unsupported Claim | Abstention | SQL Exec | Latency |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5-0.8B |  |  |  |  | - | 未测 |
| Qwen3.5-2B |  |  |  |  | - | 未测 |
| BM25 RAG baseline |  | 0.924 |  | 0.887 | - | 0.546 ms/q |
| Dense baseline |  | 0.819 |  |  | - | 1.343 ms/q |
| Hybrid RAG baseline |  | 0.876 |  |  | - | 29.439 ms/q |
| Hybrid + rerank baseline |  | 0.838 |  |  | - | 36.138 ms/q |
| Verifier baseline |  |  | 0.557 |  | - | 0.592 ms/q |
| SQL rule baseline |  |  |  |  | 1.000 | 0.345 ms/q |
| MiniGeo-Agent demo | demo | demo | 见 verifier | demo | PASS | 17.245 ms/q |

## 待补充模型结果

- Qwen3.5-2B no-RAG。
- Qwen3.5-2B + 模型 RAG。
- MiniGeo-2B-SFT。
- MiniGeo-2B-SFT + RAG + Verifier。
- Qwen3.5-4B + RAG。
