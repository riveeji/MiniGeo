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
| Qwen3-Embedding-0.6B dense retrieval |  | 0.957 |  |  | - | 见 retrieval_service_eval |
| Qwen3-Embedding-0.6B hybrid retrieval |  | 1.000 |  |  | - | 见 retrieval_service_eval |
| Qwen3-Embedding-0.6B hybrid + lexical rerank |  | 0.900 |  |  | - | 见 retrieval_service_eval |
| Qwen3-Reranker-0.6B hybrid rerank |  | 0.995 |  |  | - | 见 retrieval_service_eval |
| Qwen3.5-2B base smoke |  | 0.000 |  | 0.900 | - | 7899.095 ms/q |
| MiniGeo-2B-SFT 128step smoke |  | 0.444 |  | 1.000 | - | 0.000 ms/q |
| MiniGeo-2B-SFT json64 smoke |  | 0.000 |  | 0.100 | - | 6440.721 ms/q |
| MiniGeo-2B-SFT json64 evidence smoke |  | 1.000 |  | 1.000 | - | 8505.253 ms/q |
| BM25 RAG baseline |  | 1.000 |  | 1.000 | - | 3.080 ms/q |
| Dense baseline |  | 0.828 |  |  | - | 1.609 ms/q |
| Hybrid RAG baseline |  | 0.995 |  |  | - | 4.762 ms/q |
| Hybrid + rerank baseline |  | 0.880 |  |  | - | 16.341 ms/q |
| Verifier baseline |  |  | 0.611 |  | - | 1.036 ms/q |
| SQL rule baseline |  |  |  |  | 1.000 | 0.257 ms/q |
| Planner baseline | 1.000 |  |  |  | - | 0.007 ms/q |
| MiniGeo-Agent demo | demo | demo | 见 verifier | demo | PASS | 44.921 ms/q |
| MiniGeo-Agent multi-case | 1.000 | case | 见 agent_cases | case | PASS | 33.020 ms/q |

## 待补充模型结果

- Qwen3.5-2B no-RAG。
- Qwen3.5-2B + 模型 RAG。
- MiniGeo-2B-SFT。
- MiniGeo-2B-SFT + RAG + Verifier。
