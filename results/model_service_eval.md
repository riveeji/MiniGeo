# MiniGeo 模型服务 Smoke Eval

本报告记录 OpenAI-compatible 模型服务的小样本 RAG 评测结果。
该脚本默认只跑少量样本，用于验证服务连通性、响应格式和引用行为，不替代完整 benchmark。

- items：1
- non_empty_answer_rate：0.000
- citation_hit_rate：0.000
- empty_raw_outputs：1
- latency_ms：91719.892
- raw_outputs：`results\model_service_rag_smoke.jsonl`

## 解释

- `non_empty_answer_rate=0` 通常表示服务返回的 `message.content` 为空，或模型没有按 JSON contract 输出。
- `empty_raw_outputs>0` 说明 MiniGeo 没有收到可解析的最终回答文本。
- Ollama 的部分 thinking 模型可能把内容放入 `reasoning/thinking` 字段；MiniGeo 的 OpenAI-compatible 评测要求最终答案进入 `message.content`。
