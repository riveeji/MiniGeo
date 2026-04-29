# MiniGeo 模型服务评测

本报告记录 OpenAI-compatible 模型服务的真实调用结果，用于补充主结果表。

| Mode | Items | Non-empty | Citation Hit | Abstention Acc | Empty Raw | Request Errors | Latency | Raw Outputs |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| rag | 150 | 1.000 | 0.667 | 0.767 | 0 | 0 | 2181.328 ms/q | `results\model_service_qwen35_4b_150_rag.jsonl` |
| no-rag | 150 | 1.000 | 0.000 | 0.793 | 0 | 0 | 1997.961 ms/q | `results\model_service_qwen35_4b_150_no_rag.jsonl` |

补充 SQL Tool 结果：

- `Qwen/Qwen3.5-4B` SQL generator 在 30 条 SQL benchmark 上 `sql_exec_accuracy=1.000`
- SQL 平均延迟约 10119.747 ms/item

## 本次外部模型服务

- 服务形态：Colab A100 + vLLM OpenAI-compatible API + Cloudflare quick tunnel
- 模型：`Qwen/Qwen3.5-4B`
- `/v1/models` 连通性：通过
- 本轮通过 `MINIGEO_DISABLE_THINKING=1` 向 vLLM 发送 `chat_template_kwargs={"enable_thinking": false}`。

说明：Cloudflare quick tunnel 和 Colab runtime 都是临时服务。若 Colab 页面停止、运行时断开或 tunnel cell 被中断，本地评测需要换成新的 tunnel URL 后重新运行。

## 解释

- `non_empty_answer_rate=0` 通常表示服务返回的 `message.content` 为空，或模型没有按 JSON contract 输出。
- `citation_hit_rate` 统计模型返回 citation 与 benchmark evidence 的交集比例。
- `no-rag` 模式不提供文档证据，因此 citation hit 通常应显著低于 RAG。
- `empty_raw_outputs>0` 说明 MiniGeo 没有收到可解析的最终回答文本。
