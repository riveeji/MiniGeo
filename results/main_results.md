# MiniGeo 主结果

本表由 `scripts/write_report_artifacts.py` 生成。当前数值是本地 baseline 和 demo 结果，不代表真实 Qwen3.5 模型服务或 QLoRA 训练结果。

| System | Acc | Citation Hit | Unsupported Claim | Abstention | SQL Exec | Latency |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5-0.8B |  |  |  |  | - | 未测 |
| Qwen3.5-2B |  |  |  |  | - | 未测 |
| BM25 RAG baseline |  | 0.924 |  | 1.000 | - | 0.586 ms/q |
| Dense baseline |  | 0.819 |  |  | - | 1.369 ms/q |
| Hybrid RAG baseline |  | 0.876 |  |  | - | 30.473 ms/q |
| Hybrid + rerank baseline |  | 0.838 |  |  | - | 37.279 ms/q |
| Verifier baseline |  |  | 0.557 |  | - | 0.618 ms/q |
| SQL rule baseline |  |  |  |  | 1.000 | 0.353 ms/q |
| MiniGeo-Agent demo | demo | demo | 见 verifier | demo | PASS | 16.869 ms/q |

## 待补充模型结果

- Qwen3.5-2B no-RAG。
- Qwen3.5-2B + 模型 RAG。
- MiniGeo-2B-SFT。
- MiniGeo-2B-SFT + RAG + Verifier。
- Qwen3.5-4B + RAG。
