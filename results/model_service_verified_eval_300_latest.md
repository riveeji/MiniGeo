# MiniGeo RAG + Verifier 离线评测

本报告基于已保存的模型 RAG 输出离线生成，不会再次调用模型服务。

- output：`results\model_service_qwen35_4b_300_latest_rag_verified.jsonl`
- verifier_mode：heuristic
- items：300
- citation_hit_rate：0.679
- abstention_accuracy：0.747
- request_errors：0
- unsupported_claim_rate：0.023

## Verifier Verdicts

| Verdict | Count |
|---|---:|
| insufficient_evidence | 3 |
| partially_supported | 2 |
| skipped | 100 |
| supported | 195 |
