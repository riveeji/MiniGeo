# MiniGeo 真实检索服务消融

本报告记录 Colab A100 上分阶段运行的真实 OpenAI-compatible 检索服务结果，用于补充本地 deterministic baseline。

## 本次服务

- 日期：2026-05-04
- 服务形态：Colab A100 staged retrieval services
- 模式：先接入真实 embedding 服务，再接入真实 reranker 服务
- Embedding 模型：`Qwen/Qwen3-Embedding-0.6B`
- Reranker 模型：`Qwen/Qwen3-Reranker-0.6B`
- Embedding 命令：`python scripts/evaluate_retrieval_ablation.py --use-embedding-service`
- Reranker 命令：`python scripts/evaluate_retrieval_ablation.py --use-reranker-service --json-output results/retrieval_service_eval_reranker.json --markdown-output results/retrieval_service_eval_reranker.md`

## 结果

| System | Recall@5 | Recall@10 | MRR | Citation Hit | Latency |
|---|---:|---:|---:|---:|---:|
| Qwen3-Embedding dense retrieval | 0.885 | 0.957 | 0.644 | 0.957 | 1683.670 ms/q |
| Qwen3-Embedding hybrid retrieval | 0.962 | 1.000 | 0.738 | 1.000 | 5.773 ms/q |
| Qwen3-Embedding hybrid + local lexical rerank | 0.617 | 0.900 | 0.474 | 0.900 | 12.393 ms/q |
| Qwen3-Reranker-0.6B hybrid rerank | 0.876 | 0.995 | 0.545 | 0.995 | 45.068 ms/q |

## 解释

- 当前 42 条 seed corpus 上，BM25 + query expansion 仍然很强；真实 dense 单独使用时低于 BM25。
- Hybrid 能把真实 embedding staged run 的 `recall@10` 和 `citation_hit_rate` 拉回到 1.000，说明 dense 可以作为补充通道。
- 本地 lexical reranker 会把 `citation_hit_rate` 拉低到 0.900，不适合作为主链路。
- 真实 `Qwen/Qwen3-Reranker-0.6B` 把 hybrid rerank 的 `citation_hit_rate` 提升到 0.995，基本修复了本地 lexical reranker 的 gold evidence 降排问题。
- 两轮服务是 staged run：embedding 与 reranker 没有同时接入同一个服务组合。正式延迟结论仍需单独做 cold/warm latency 评测。
