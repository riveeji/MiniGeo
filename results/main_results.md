# MiniGeo 主结果

本表由 `scripts/write_report_artifacts.py` 生成，包含本地 baseline、demo 结果，以及已保存的真实模型服务结果。

| System | Acc | Citation Hit | Unsupported Claim | Abstention | SQL Exec | Latency |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5-0.8B |  |  |  |  | - | 未测 |
| Qwen3.5-2B |  |  |  |  | - | 未测 |
| Qwen3.5-4B no-RAG |  | 0.000 |  | 0.793 | - | 见 model_service_eval |
| Qwen3.5-4B + BM25 RAG |  | 0.667 |  | 0.767 | - | 见 model_service_eval |
| Qwen3.5-4B + BM25 RAG + Verifier |  | 0.667 | 0.017 | 0.767 | - | 见 model_service_verified_eval |
| Qwen3.5-4B SQL generator |  |  |  |  | 1.000 | 见 model_service_eval |
| BM25 RAG baseline |  | 1.000 |  | 1.000 | - | 3.813 ms/q |
| Dense baseline |  | 0.828 |  |  | - | 1.948 ms/q |
| Hybrid RAG baseline |  | 0.995 |  |  | - | 63.791 ms/q |
| Hybrid + rerank baseline |  | 0.880 |  |  | - | 77.703 ms/q |
| Verifier baseline |  |  | 0.611 |  | - | 1.281 ms/q |
| SQL rule baseline |  |  |  |  | 1.000 | 0.431 ms/q |
| Planner baseline | 1.000 |  |  |  | - | 0.008 ms/q |
| MiniGeo-Agent demo | demo | demo | 见 verifier | demo | PASS | 55.970 ms/q |

## 待补充模型结果

- Qwen3.5-2B no-RAG。
- Qwen3.5-2B + 模型 RAG。
- MiniGeo-2B-SFT。
- MiniGeo-2B-SFT + RAG + Verifier。
- Qwen3.5-4B + RAG 的 300 题全量模型服务结果。
