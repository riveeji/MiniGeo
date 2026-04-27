# MiniGeo 失败案例

本文件由 `scripts/write_report_artifacts.py` 生成，用于沉淀检索、Verifier、SQL 和 Agent 的可复查失败样例。

```text
case_id: retrieval_001
question: 为什么需要 failure case analysis？
system: BM25 RAG baseline
observed_output: doc_pyrite#chunk_002, doc_muscovite#chunk_002, doc_dolomite#chunk_002, doc_system#chunk_011, doc_olivine#chunk_002
expected_behavior: doc_system#chunk_005
failure_type: retrieval_miss
suspected_cause: tokenizer、同义词或语料覆盖不足
next_action: 补充同义词、改进 query rewrite，或增加对应公开资料 chunk。
```

```text
case_id: retrieval_002
question: 识别长石时为什么需要证据来源？
system: BM25 RAG baseline
observed_output: doc_muscovite#chunk_002, doc_quartz#chunk_002, doc_system#chunk_001, doc_anorthite#chunk_002, doc_olivine#chunk_002
expected_behavior: doc_feldspar#chunk_001
failure_type: retrieval_miss
suspected_cause: tokenizer、同义词或语料覆盖不足
next_action: 补充同义词、改进 query rewrite，或增加对应公开资料 chunk。
```

```text
case_id: retrieval_003
question: MiniGeo 如何避免在回答石英问题时产生无证据结论？
system: BM25 RAG baseline
observed_output: doc_anorthite#chunk_002, doc_system#chunk_006, doc_system#chunk_001, doc_system#chunk_012, doc_system#chunk_007
expected_behavior: doc_quartz#chunk_001
failure_type: retrieval_miss
suspected_cause: tokenizer、同义词或语料覆盖不足
next_action: 补充同义词、改进 query rewrite，或增加对应公开资料 chunk。
```

```text
case_id: retrieval_004
question: MiniGeo 如何避免在回答长石问题时产生无证据结论？
system: BM25 RAG baseline
observed_output: doc_anorthite#chunk_002, doc_system#chunk_006, doc_system#chunk_001, doc_system#chunk_012, doc_system#chunk_007
expected_behavior: doc_feldspar#chunk_001
failure_type: retrieval_miss
suspected_cause: tokenizer、同义词或语料覆盖不足
next_action: 补充同义词、改进 query rewrite，或增加对应公开资料 chunk。
```

```text
case_id: retrieval_005
question: MiniGeo 如何避免在回答方解石问题时产生无证据结论？
system: BM25 RAG baseline
observed_output: doc_system#chunk_006, doc_anorthite#chunk_002, doc_system#chunk_001, doc_system#chunk_012, doc_calcite#chunk_003
expected_behavior: doc_calcite#chunk_001
failure_type: retrieval_miss
suspected_cause: tokenizer、同义词或语料覆盖不足
next_action: 补充同义词、改进 query rewrite，或增加对应公开资料 chunk。
```

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
