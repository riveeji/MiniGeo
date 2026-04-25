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
