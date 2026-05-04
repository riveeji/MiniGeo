# MiniGeo 主结果

本表由 `scripts/write_report_artifacts.py` 生成，包含本地 baseline、demo 结果，以及已保存的真实模型服务结果。

| System | Acc | Citation Hit | Unsupported Claim | Abstention | SQL Exec | Latency |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5-0.8B |  |  |  |  | - | 未测 |
| Qwen3.5-2B |  |  |  |  | - | 未测 |
| Qwen3.5-4B no-RAG |  | 0.000 |  | 0.783 | - | 见 model_service_eval |
| Qwen3.5-4B + BM25 RAG |  | 0.689 |  | 0.763 | - | 见 model_service_eval |
| Qwen3.5-4B + BM25 RAG + Verifier |  | 0.679 | 0.023 | 0.747 | - | 见 model_service_verified_eval |
| Qwen3.5-4B + BM25 RAG + Model Verifier |  | 0.665 | 0.022 | 0.740 | - | 见 model_service_model_verified_eval |
| Qwen3.5-4B SQL generator |  |  |  |  | 1.000 | 见 model_service_eval |
| BM25 RAG baseline |  | 1.000 |  | 1.000 | - | 1.974 ms/q |
| Dense baseline |  | 0.828 |  |  | - | 1.438 ms/q |
| Hybrid RAG baseline |  | 0.995 |  |  | - | 33.347 ms/q |
| Hybrid + rerank baseline |  | 0.880 |  |  | - | 39.637 ms/q |
| Verifier baseline |  |  | 0.611 |  | - | 0.622 ms/q |
| SQL rule baseline |  |  |  |  | 1.000 | 0.237 ms/q |
| Planner baseline | 1.000 |  |  |  | - | 0.007 ms/q |
| MiniGeo-Agent demo | demo | demo | 见 verifier | demo | PASS | 27.627 ms/q |

## 待补充模型结果

- Qwen3.5-2B no-RAG。
- Qwen3.5-2B + 模型 RAG。
- MiniGeo-2B-SFT。
- MiniGeo-2B-SFT + RAG + Verifier。
- 真实 Qwen3-Embedding / Qwen3-Reranker 服务消融结果。
