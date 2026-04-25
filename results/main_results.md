# MiniGeo 主结果

本表包含本地 baseline、demo 结果，以及通过 Colab A100 + vLLM 跑出的 Qwen3.5-4B 小规模真实模型服务结果。

| System | Acc | Citation Hit | Unsupported Claim | Abstention | SQL Exec | Latency |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5-0.8B |  |  |  |  | - | 未测 |
| Qwen3.5-2B |  |  |  |  | - | 未测 |
| Qwen3.5-4B no-RAG |  | 0.000 |  | 0.267 | - | 10742.210 ms/q |
| Qwen3.5-4B + BM25 RAG |  | 0.833 |  | 0.900 | - | 12843.900 ms/q |
| BM25 RAG baseline |  | 0.924 |  | 1.000 | - | 0.652 ms/q |
| Dense baseline |  | 0.819 |  |  | - | 1.570 ms/q |
| Hybrid RAG baseline |  | 0.876 |  |  | - | 36.298 ms/q |
| Hybrid + rerank baseline |  | 0.838 |  |  | - | 46.413 ms/q |
| Verifier baseline |  |  | 0.557 |  | - | 0.758 ms/q |
| SQL rule baseline |  |  |  |  | 1.000 | 0.443 ms/q |
| Qwen3.5-4B SQL generator |  |  |  |  | 1.000 | 10119.747 ms/q |
| Planner baseline | 1.000 |  |  |  | - | 0.009 ms/q |
| MiniGeo-Agent demo | demo | demo | 见 verifier | demo | PASS | 22.928 ms/q |

## 待补充模型结果

- Qwen3.5-2B no-RAG。
- Qwen3.5-2B + 模型 RAG。
- MiniGeo-2B-SFT。
- MiniGeo-2B-SFT + RAG + Verifier。

## 当前模型服务结果说明

- Qwen3.5-4B 结果基于 30 条 evidence-labeled benchmark 子集。
- RAG 相比 no-RAG 明显提升 citation hit：0.833 vs 0.000。
- RAG 的拒答准确率也更高：0.900 vs 0.267。
- 当前 vLLM/Qwen3.5-4B 输出仍存在 `Thinking Process` 泄漏，后续应优先尝试禁用 thinking 或调整 chat template。
