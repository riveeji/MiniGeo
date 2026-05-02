# MiniGeo RAG + Verifier 离线评测

本报告基于已保存的模型 RAG 输出离线生成，不会再次调用模型服务。

- output：`results\model_service_qwen35_4b_300_latest_rag_model_verified.jsonl`
- verifier_mode：model
- items：300
- citation_hit_rate：0.665
- abstention_accuracy：0.740
- request_errors：0
- unsupported_claim_rate：0.022

## Verifier Verdicts

| Verdict | Count |
|---|---:|
| contradicted | 2 |
| insufficient_evidence | 4 |
| partially_supported | 1 |
| skipped | 100 |
| supported | 193 |
