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
observed_output: answer 正确为“二氧化硅 SiO2”，但 citations 为空。
expected_behavior: citations 应包含 doc_quartz#chunk_001。
failure_type: citation_omission
suspected_cause: 模型在 Thinking Process 中分析了证据，但最终 JSON 没有稳定保留 citation 字段。
next_action: 禁用 thinking、强化 JSON-only chat template，并在 parser 中拒绝无 citation 的 answerable 输出。
```

```text
case_id: model_service_002
question: 石英和方解石在矿物类别上有什么区别？
system: Qwen3.5-4B + BM25 RAG
observed_output: 输出包含 Thinking Process，citations 命中的是检索到的相邻性质 chunk，而不是 benchmark 期望的类别 chunk。
expected_behavior: citations 应包含 doc_quartz#chunk_001 或 doc_calcite#chunk_001。
failure_type: citation_mismatch_and_format_violation
suspected_cause: BM25 召回偏向“石英/方解石对比”文本，模型又泄漏推理过程，导致 citation hit 不稳定。
next_action: 增加类别型 query rewrite，加入 reranker，并约束最终输出只保留 JSON。
```

```text
case_id: model_service_003
question: 为什么需要 failure case analysis？
system: Qwen3.5-4B + BM25 RAG
observed_output: citations 指向多个矿物性质 chunk，没有命中 doc_system#chunk_005。
expected_behavior: 应引用 failure analysis 的系统说明 chunk。
failure_type: retrieval_miss
suspected_cause: 英文术语 failure case analysis 与中文系统说明 chunk 的词面匹配弱。
next_action: 为系统方法类问题补充双语关键词，或在 hybrid retrieval 中提高 dense retrieval 权重。
```
