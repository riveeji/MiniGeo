# MiniGeo 失败案例

本文件由 `scripts/write_report_artifacts.py` 生成，用于沉淀检索、Verifier、SQL 和 Agent 的可复查失败样例。

```text
case_id: model_service_001
question: 石英的主要化学成分是什么？
system: Qwen3.5-4B + BM25 RAG
observed_output: citations=[]; answer=二氧化硅 SiO2
expected_behavior: doc_quartz#chunk_001
failure_type: model_citation_miss
suspected_cause: 模型输出格式和 citation 字段不稳定，或检索 chunk 与 benchmark gold evidence 不一致。
next_action: 禁用 thinking、强化 JSON-only 输出，并在 10 题 smoke test 达标后再跑 300 题模型评测。
```

```text
case_id: model_service_002
question: 赤铁矿的矿物类别是什么？
system: Qwen3.5-4B + BM25 RAG
observed_output: citations=[]; answer=铁氧化物矿物
expected_behavior: doc_hematite#chunk_001
failure_type: model_citation_miss
suspected_cause: 模型输出格式和 citation 字段不稳定，或检索 chunk 与 benchmark gold evidence 不一致。
next_action: 禁用 thinking、强化 JSON-only 输出，并在 10 题 smoke test 达标后再跑 300 题模型评测。
```

```text
case_id: model_service_003
question: 石英和方解石在矿物类别上有什么区别？
system: Qwen3.5-4B + BM25 RAG
observed_output: citations=['doc_calcite#chunk_002', 'doc_calcite#chunk_003', 'doc_dolomite#chunk_002', 'doc_gypsum#chunk_002', 'doc_quartz#chunk_003']; answer=Thinking Process:  1.  **Analyze the Request:**     *   Task: Answer a geoscience question using *only* the provided evidence.     *   Constraint 1: If evidence is insufficient, re
expected_behavior: doc_calcite#chunk_001, doc_quartz#chunk_001
failure_type: model_citation_miss
suspected_cause: 模型输出格式和 citation 字段不稳定，或检索 chunk 与 benchmark gold evidence 不一致。
next_action: 禁用 thinking、强化 JSON-only 输出，并在 10 题 smoke test 达标后再跑 300 题模型评测。
```
