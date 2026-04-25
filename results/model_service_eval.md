# MiniGeo 模型服务 Smoke Eval

本报告记录 OpenAI-compatible 模型服务的小样本 RAG 评测结果。
该脚本默认只跑少量样本，用于验证服务连通性、响应格式和引用行为，不替代完整 benchmark。

- items：3
- non_empty_answer_rate：1.000
- citation_hit_rate：0.667
- empty_raw_outputs：0
- latency_ms：10213.183
- raw_outputs：`results\model_service_rag_smoke.jsonl`

## 本次外部模型服务

- 服务形态：Colab A100 + vLLM OpenAI-compatible API + Cloudflare quick tunnel
- 模型：`Qwen/Qwen3.5-4B`
- `/v1/models` 连通性：通过
- RAG smoke eval：3 条样本全部返回非空答案，citation hit rate 为 0.667
- SQL model eval：30 条 SQL benchmark 全部执行正确，`sql_exec_accuracy=1.000`
- SQL 平均延迟：约 10119.747 ms/item

说明：Cloudflare quick tunnel 和 Colab runtime 都是临时服务。若 Colab 页面停止、运行时断开或 tunnel cell 被中断，本地评测需要换成新的 tunnel URL 后重新运行。

## 解释

- `non_empty_answer_rate=0` 通常表示服务返回的 `message.content` 为空，或模型没有按 JSON contract 输出。
- `empty_raw_outputs>0` 说明 MiniGeo 没有收到可解析的最终回答文本。
- Ollama 的部分 thinking 模型可能把内容放入 `reasoning/thinking` 字段；MiniGeo 的 OpenAI-compatible 评测要求最终答案进入 `message.content`。
