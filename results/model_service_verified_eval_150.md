# MiniGeo RAG + Verifier 离线评测

本报告基于已保存的模型 RAG 输出离线生成，不会再次调用模型服务。

- output：`results\model_service_qwen35_4b_150_rag_verified.jsonl`
- items：150
- citation_hit_rate：0.667
- abstention_accuracy：0.767
- request_errors：0
- unsupported_claim_rate：0.017

## Verifier Verdicts

| Verdict | Count |
|---|---:|
| insufficient_evidence | 2 |
| skipped | 44 |
| supported | 104 |
