# MiniGeo 失败案例

本文件由 `scripts/write_report_artifacts.py` 生成，用于沉淀检索、Verifier、SQL 和 Agent 的可复查失败样例。

```text
case_id: model_service_001
question: 秦皇岛错误预测样本的可能光谱原因是什么？
system: Qwen3.5-4B + BM25 RAG
observed_output: citations=[]; answer=证据不足
expected_behavior: doc_feldspar#chunk_002, doc_quartz#chunk_002, doc_spectroscopy#chunk_003
failure_type: model_citation_miss
suspected_cause: 模型最终回答使用了相关但非 gold 的 chunk，或在证据不足场景中过早拒答。
next_action: 复查 citation miss 样例，比较 BM25 top-k 与模型实际引用；后续用 reranker、Verifier 或更严格 citation prompt 降低 miss。
```

```text
case_id: model_service_002
question: 识别石英时为什么需要证据来源？
system: Qwen3.5-4B + BM25 RAG
observed_output: citations=['doc_quartz#chunk_002', 'doc_system#chunk_001']; answer=识别石英时需要证据来源，因为可信的回答需要可追踪的证据来支持结论，例如石英的强拉曼峰接近464 cm-1可作为重要光谱证据，同时返回证据来源便于检查引用是否支持结论。
expected_behavior: doc_quartz#chunk_001
failure_type: model_citation_miss
suspected_cause: 模型最终回答使用了相关但非 gold 的 chunk，或在证据不足场景中过早拒答。
next_action: 复查 citation miss 样例，比较 BM25 top-k 与模型实际引用；后续用 reranker、Verifier 或更严格 citation prompt 降低 miss。
```

```text
case_id: model_service_003
question: 长石的常用组成或化学式是什么？
system: Qwen3.5-4B + BM25 RAG
observed_output: citations=['doc_anorthite#chunk_001']; answer=长石的化学组成可表示为 CaAl2Si2O8（以钙长石为例）。
expected_behavior: doc_feldspar#chunk_001
failure_type: model_citation_miss
suspected_cause: 模型最终回答使用了相关但非 gold 的 chunk，或在证据不足场景中过早拒答。
next_action: 复查 citation miss 样例，比较 BM25 top-k 与模型实际引用；后续用 reranker、Verifier 或更严格 citation prompt 降低 miss。
```
