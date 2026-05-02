# MiniGeo 失败案例

本文件由 `scripts/write_report_artifacts.py` 生成，用于沉淀检索、Verifier、SQL 和 Agent 的可复查失败样例。

```text
case_id: model_service_001
question: 秦皇岛错误预测样本的可能光谱原因是什么？
system: Qwen3.5-4B + BM25 RAG
observed_output: citations=[]; answer=证据不足以确定秦皇岛错误预测样本的具体光谱原因，因为提供的材料仅包含通用系统说明、赤铁矿和石英的光谱特征描述以及拉曼光谱的一般影响因素，未提及秦皇岛样本的具体光谱数据或错误类型。
expected_behavior: doc_feldspar#chunk_002, doc_quartz#chunk_002, doc_spectroscopy#chunk_003
failure_type: model_citation_miss
suspected_cause: 模型最终回答使用了相关但非 gold 的 chunk，或在证据不足场景中过早拒答。
next_action: 复查 citation miss 样例，比较 BM25 top-k 与模型实际引用；后续用 reranker、Verifier 或更严格 citation prompt 降低 miss。
```

```text
case_id: model_service_002
question: 为什么开放资料需要记录 URL 和 license？
system: Qwen3.5-4B + BM25 RAG
observed_output: citations=['doc_pyrite#chunk_002']; answer=开放资料需要记录 URL 和 license，以便控制来源追踪和版权风险。
expected_behavior: doc_system#chunk_002
failure_type: model_citation_miss
suspected_cause: 模型最终回答使用了相关但非 gold 的 chunk，或在证据不足场景中过早拒答。
next_action: 复查 citation miss 样例，比较 BM25 top-k 与模型实际引用；后续用 reranker、Verifier 或更严格 citation prompt 降低 miss。
```

```text
case_id: model_service_003
question: 为什么说 MiniGeo 的贡献不是模型规模？
system: Qwen3.5-4B + BM25 RAG
observed_output: citations=['doc_calcite#chunk_001']; answer=MiniGeo 的贡献在于构建 benchmark、RAG、证据验证和数据分析闭环，而非训练新的地学基础模型。
expected_behavior: doc_system#chunk_004
failure_type: model_citation_miss
suspected_cause: 模型最终回答使用了相关但非 gold 的 chunk，或在证据不足场景中过早拒答。
next_action: 复查 citation miss 样例，比较 BM25 top-k 与模型实际引用；后续用 reranker、Verifier 或更严格 citation prompt 降低 miss。
```
