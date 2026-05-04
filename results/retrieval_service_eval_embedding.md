# MiniGeo 真实检索服务消融

本报告记录真实 OpenAI-compatible 检索服务的调用结果，用于补充本地 deterministic baseline。

## 本次服务

- 日期：2026-05-04
- 服务形态：Colab A100 + vLLM OpenAI-compatible API + Cloudflare quick tunnel
- 模式：只接入真实 embedding 服务，reranker 仍使用本地 lexical reranker
- 模型：`Qwen/Qwen3-Embedding-0.6B`
- 命令：`python scripts/evaluate_retrieval_ablation.py --use-embedding-service`

## 结果

| System | Recall@5 | Recall@10 | MRR | Citation Hit | Latency |
|---|---:|---:|---:|---:|---:|
| BM25 | 0.976 | 1.000 | 0.774 | 1.000 | 2.594 ms/q |
| Qwen3-Embedding dense | 0.885 | 0.957 | 0.644 | 0.957 | 1683.670 ms/q |
| BM25 + Qwen3-Embedding hybrid | 0.962 | 1.000 | 0.738 | 1.000 | 5.773 ms/q |
| Hybrid + local lexical rerank | 0.617 | 0.900 | 0.474 | 0.900 | 12.393 ms/q |

## 解释

- 当前 42 条 seed corpus 上，BM25 + query expansion 仍然很强；真实 dense 单独使用时低于 BM25。
- Hybrid 能把 `recall@10` 和 `citation_hit_rate` 拉回到 1.000，说明 dense 可以作为补充通道，但当前还没有证明它优于 BM25。
- 本地 lexical reranker 在这轮结果中显著拉低检索，因此暂时不应作为主结果保留；下一步需要接入 `Qwen/Qwen3-Reranker-0.6B` 做真实 reranker 消融。
- 本轮为 staged service run，embedding 客户端会按文本缓存请求；hybrid 和 rerank 的延迟是 warm-cache 值，正式延迟结论需要单独做 cold/warm latency 评测。
