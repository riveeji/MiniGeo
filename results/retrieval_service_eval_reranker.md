# MiniGeo 真实检索服务消融

本报告记录真实 OpenAI-compatible 检索服务的调用结果，用于补充本地 deterministic baseline。

## 本次服务

- 日期：2026-05-04
- 模式：`reranker_service`
- Embedding 模型：`Qwen/Qwen3-Embedding-0.6B`
- Reranker 模型：`Qwen/Qwen3-Reranker-0.6B`
- 命令：`python scripts/evaluate_retrieval_ablation.py --use-reranker-service --json-output results/retrieval_service_eval_reranker.json --markdown-output results/retrieval_service_eval_reranker.md`

## 结果

| System | Recall@5 | Recall@10 | MRR | Citation Hit | Latency |
|---|---:|---:|---:|---:|---:|
| Qwen3-Reranker-0.6B hybrid rerank | 0.876 | 0.995 | 0.545 | 0.995 | 45.068 ms/q |

## 解释

- 本轮只接入真实 reranker 服务，dense embedding 仍为本地 deterministic baseline。
