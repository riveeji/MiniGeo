# MiniGeo 检索失败分析

本报告分析 evidence-labeled benchmark 上各检索系统的 top-k miss case，用于区分 tokenizer、语料、evidence label 和 reranker 排序问题。

## 汇总

| System | Items | Misses | Miss Rate | Categories |
|---|---:|---:|---:|---|
| bm25 | 209 | 0 | 0.000 | - |
| dense | 209 | 36 | 0.172 | evidence_label_narrow=20, retrieval_gold_missing=2, same_topic_wrong_chunk=14 |
| hybrid | 209 | 0 | 0.000 | - |
| hybrid_rerank | 209 | 25 | 0.120 | reranker_demoted_gold=25 |

## 样例

```text
system: dense
id: minigeo_015
question: 长石通常包含哪些结构特征？
expected_evidence: doc_feldspar#chunk_001
retrieved_ids: doc_anorthite#chunk_002, doc_olivine#chunk_002, doc_anorthite#chunk_001, doc_quartz#chunk_003, doc_magnetite#chunk_002, doc_system#chunk_001, doc_spectroscopy#chunk_001, doc_calcite#chunk_002, doc_kaolinite#chunk_002, doc_gypsum#chunk_001
category: same_topic_wrong_chunk
suspected_cause: 检索到了同 topic 的 chunk，但排序没有命中精确证据。
next_action: 补充更细粒度 query expansion、chunk metadata 或 reranker 特征。
```

```text
system: dense
id: minigeo_016
question: 一个样本既有 464 cm-1 附近峰又被模型判为长石时，应该如何解释？
expected_evidence: doc_quartz#chunk_002, doc_feldspar#chunk_002, doc_spectroscopy#chunk_003
retrieved_ids: doc_anorthite#chunk_002, doc_anorthite#chunk_001, doc_system#chunk_008, doc_kaolinite#chunk_001, doc_olivine#chunk_001, doc_feldspar#chunk_001, doc_quartz#chunk_003, doc_quartz#chunk_001, doc_dolomite#chunk_002, doc_system#chunk_001
category: evidence_label_narrow
suspected_cause: 检索到了同一文档的相关 chunk，但 benchmark 只标了更窄的 gold chunk。
next_action: 人工复核 retrieved chunk 是否也能支撑答案；若能支撑，应扩充 evidence label。
```

```text
system: dense
id: minigeo_038
question: 为什么需要 failure case analysis？
expected_evidence: doc_system#chunk_005
retrieved_ids: doc_gypsum#chunk_001, doc_hematite#chunk_001, doc_pyrite#chunk_001, doc_olivine#chunk_001, doc_pyrite#chunk_002, doc_dolomite#chunk_001, doc_system#chunk_011, doc_muscovite#chunk_001, doc_calcite#chunk_001, doc_magnetite#chunk_001
category: evidence_label_narrow
suspected_cause: 检索到了同一文档的相关 chunk，但 benchmark 只标了更窄的 gold chunk。
next_action: 人工复核 retrieved chunk 是否也能支撑答案；若能支撑，应扩充 evidence label。
```

```text
system: dense
id: minigeo_050
question: 为什么最终报告要包含 latency？
expected_evidence: doc_system#chunk_010
retrieved_ids: doc_gypsum#chunk_001, doc_pyrite#chunk_001, doc_anorthite#chunk_001, doc_magnetite#chunk_001, doc_anorthite#chunk_002, doc_magnetite#chunk_002, doc_olivine#chunk_001, doc_quartz#chunk_002, doc_quartz#chunk_003, doc_hematite#chunk_001
category: retrieval_gold_missing
suspected_cause: 检索排序未把 gold evidence 放入 top-k。
next_action: 扩充语料、改进检索融合权重或提高 candidate_k。
```

```text
system: dense
id: minigeo_051
question: 石英属于哪类矿物？
expected_evidence: doc_quartz#chunk_001
retrieved_ids: doc_anorthite#chunk_002, doc_calcite#chunk_001, doc_hematite#chunk_001, doc_kaolinite#chunk_001, doc_quartz#chunk_003, doc_feldspar#chunk_001, doc_magnetite#chunk_001, doc_dolomite#chunk_001, doc_quartz#chunk_002, doc_gypsum#chunk_002
category: evidence_label_narrow
suspected_cause: 检索到了同一文档的相关 chunk，但 benchmark 只标了更窄的 gold chunk。
next_action: 人工复核 retrieved chunk 是否也能支撑答案；若能支撑，应扩充 evidence label。
```

```text
system: dense
id: minigeo_056
question: 识别长石时为什么需要证据来源？
expected_evidence: doc_feldspar#chunk_001
retrieved_ids: doc_muscovite#chunk_002, doc_olivine#chunk_002, doc_pyrite#chunk_002, doc_spectroscopy#chunk_001, doc_anorthite#chunk_002, doc_quartz#chunk_002, doc_system#chunk_001, doc_spectroscopy#chunk_003, doc_olivine#chunk_001, doc_anorthite#chunk_001
category: same_topic_wrong_chunk
suspected_cause: 检索到了同 topic 的 chunk，但排序没有命中精确证据。
next_action: 补充更细粒度 query expansion、chunk metadata 或 reranker 特征。
```

```text
system: dense
id: minigeo_058
question: 方解石的常用组成或化学式是什么？
expected_evidence: doc_calcite#chunk_001
retrieved_ids: doc_pyrite#chunk_001, doc_magnetite#chunk_001, doc_gypsum#chunk_001, doc_dolomite#chunk_001, doc_calcite#chunk_002, doc_gypsum#chunk_002, doc_feldspar#chunk_001, doc_anorthite#chunk_001, doc_dolomite#chunk_002, doc_system#chunk_001
category: evidence_label_narrow
suspected_cause: 检索到了同一文档的相关 chunk，但 benchmark 只标了更窄的 gold chunk。
next_action: 人工复核 retrieved chunk 是否也能支撑答案；若能支撑，应扩充 evidence label。
```

```text
system: dense
id: minigeo_059
question: 识别方解石时为什么需要证据来源？
expected_evidence: doc_calcite#chunk_001
retrieved_ids: doc_muscovite#chunk_002, doc_quartz#chunk_002, doc_olivine#chunk_002, doc_spectroscopy#chunk_001, doc_system#chunk_001, doc_dolomite#chunk_002, doc_pyrite#chunk_002, doc_calcite#chunk_002, doc_quartz#chunk_003, doc_gypsum#chunk_002
category: evidence_label_narrow
suspected_cause: 检索到了同一文档的相关 chunk，但 benchmark 只标了更窄的 gold chunk。
next_action: 人工复核 retrieved chunk 是否也能支撑答案；若能支撑，应扩充 evidence label。
```

```text
system: dense
id: minigeo_082
question: 高岭石的常用组成或化学式是什么？
expected_evidence: doc_kaolinite#chunk_001
retrieved_ids: doc_dolomite#chunk_001, doc_pyrite#chunk_001, doc_magnetite#chunk_001, doc_gypsum#chunk_001, doc_feldspar#chunk_001, doc_anorthite#chunk_001, doc_olivine#chunk_001, doc_pyrite#chunk_002, doc_quartz#chunk_001, doc_calcite#chunk_002
category: same_topic_wrong_chunk
suspected_cause: 检索到了同 topic 的 chunk，但排序没有命中精确证据。
next_action: 补充更细粒度 query expansion、chunk metadata 或 reranker 特征。
```

```text
system: dense
id: minigeo_098
question: 如果问题声称钙长石是碳酸盐矿物，但证据显示其属于长石族硅酸盐，系统应如何回答？
expected_evidence: doc_anorthite#chunk_001
retrieved_ids: doc_anorthite#chunk_002, doc_calcite#chunk_001, doc_hematite#chunk_001, doc_kaolinite#chunk_001, doc_quartz#chunk_003, doc_kaolinite#chunk_002, doc_olivine#chunk_001, doc_muscovite#chunk_001, doc_feldspar#chunk_001, doc_feldspar#chunk_002
category: evidence_label_narrow
suspected_cause: 检索到了同一文档的相关 chunk，但 benchmark 只标了更窄的 gold chunk。
next_action: 人工复核 retrieved chunk 是否也能支撑答案；若能支撑，应扩充 evidence label。
```

```text
system: hybrid_rerank
id: minigeo_038
question: 为什么需要 failure case analysis？
expected_evidence: doc_system#chunk_005
retrieved_ids: doc_pyrite#chunk_002, doc_system#chunk_011, doc_dolomite#chunk_002, doc_olivine#chunk_002, doc_muscovite#chunk_002, doc_gypsum#chunk_001, doc_pyrite#chunk_001, doc_anorthite#chunk_002, doc_dolomite#chunk_001, doc_quartz#chunk_001
category: reranker_demoted_gold
suspected_cause: reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。
next_action: 检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。
```

```text
system: hybrid_rerank
id: minigeo_050
question: 为什么最终报告要包含 latency？
expected_evidence: doc_system#chunk_010
retrieved_ids: doc_magnetite#chunk_002, doc_system#chunk_006, doc_gypsum#chunk_001, doc_dolomite#chunk_002, doc_quartz#chunk_002, doc_pyrite#chunk_002, doc_pyrite#chunk_001, doc_anorthite#chunk_001, doc_magnetite#chunk_001, doc_anorthite#chunk_002
category: reranker_demoted_gold
suspected_cause: reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。
next_action: 检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。
```

```text
system: hybrid_rerank
id: minigeo_056
question: 识别长石时为什么需要证据来源？
expected_evidence: doc_feldspar#chunk_001
retrieved_ids: doc_muscovite#chunk_002, doc_quartz#chunk_002, doc_olivine#chunk_002, doc_system#chunk_001, doc_pyrite#chunk_002, doc_spectroscopy#chunk_001, doc_anorthite#chunk_002, doc_anorthite#chunk_001, doc_system#chunk_006, doc_system#chunk_002
category: reranker_demoted_gold
suspected_cause: reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。
next_action: 检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。
```

```text
system: hybrid_rerank
id: minigeo_098
question: 如果问题声称钙长石是碳酸盐矿物，但证据显示其属于长石族硅酸盐，系统应如何回答？
expected_evidence: doc_anorthite#chunk_001
retrieved_ids: doc_anorthite#chunk_002, doc_calcite#chunk_001, doc_kaolinite#chunk_001, doc_feldspar#chunk_001, doc_hematite#chunk_001, doc_olivine#chunk_001, doc_dolomite#chunk_001, doc_kaolinite#chunk_002, doc_feldspar#chunk_002, doc_quartz#chunk_003
category: reranker_demoted_gold
suspected_cause: reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。
next_action: 检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。
```

```text
system: hybrid_rerank
id: minigeo_135
question: MiniGeo 如何避免在回答石英问题时产生无证据结论？
expected_evidence: doc_quartz#chunk_001
retrieved_ids: doc_system#chunk_006, doc_system#chunk_001, doc_anorthite#chunk_002, doc_olivine#chunk_002, doc_spectroscopy#chunk_003, doc_system#chunk_007, doc_muscovite#chunk_002, doc_quartz#chunk_002, doc_magnetite#chunk_002, doc_system#chunk_012
category: reranker_demoted_gold
suspected_cause: reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。
next_action: 检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。
```

```text
system: hybrid_rerank
id: minigeo_136
question: MiniGeo 如何避免在回答长石问题时产生无证据结论？
expected_evidence: doc_feldspar#chunk_001
retrieved_ids: doc_anorthite#chunk_002, doc_system#chunk_006, doc_system#chunk_001, doc_olivine#chunk_002, doc_spectroscopy#chunk_003, doc_system#chunk_007, doc_muscovite#chunk_002, doc_magnetite#chunk_002, doc_system#chunk_012, doc_system#chunk_009
category: reranker_demoted_gold
suspected_cause: reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。
next_action: 检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。
```

```text
system: hybrid_rerank
id: minigeo_137
question: MiniGeo 如何避免在回答方解石问题时产生无证据结论？
expected_evidence: doc_calcite#chunk_001
retrieved_ids: doc_system#chunk_006, doc_system#chunk_001, doc_anorthite#chunk_002, doc_muscovite#chunk_002, doc_olivine#chunk_002, doc_spectroscopy#chunk_003, doc_system#chunk_007, doc_calcite#chunk_003, doc_magnetite#chunk_002, doc_calcite#chunk_002
category: reranker_demoted_gold
suspected_cause: reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。
next_action: 检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。
```

```text
system: hybrid_rerank
id: minigeo_138
question: MiniGeo 如何避免在回答赤铁矿问题时产生无证据结论？
expected_evidence: doc_hematite#chunk_001
retrieved_ids: doc_magnetite#chunk_002, doc_system#chunk_006, doc_system#chunk_001, doc_spectroscopy#chunk_003, doc_anorthite#chunk_002, doc_olivine#chunk_002, doc_pyrite#chunk_002, doc_system#chunk_007, doc_muscovite#chunk_002, doc_hematite#chunk_002
category: reranker_demoted_gold
suspected_cause: reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。
next_action: 检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。
```

```text
system: hybrid_rerank
id: minigeo_140
question: MiniGeo 如何避免在回答石膏问题时产生无证据结论？
expected_evidence: doc_gypsum#chunk_001
retrieved_ids: doc_system#chunk_006, doc_system#chunk_001, doc_anorthite#chunk_002, doc_olivine#chunk_002, doc_spectroscopy#chunk_003, doc_muscovite#chunk_002, doc_system#chunk_007, doc_magnetite#chunk_002, doc_system#chunk_012, doc_system#chunk_009
category: reranker_demoted_gold
suspected_cause: reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。
next_action: 检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。
```

```text
system: hybrid_rerank
id: minigeo_145
question: MiniGeo 如何避免在回答高岭石问题时产生无证据结论？
expected_evidence: doc_kaolinite#chunk_001
retrieved_ids: doc_system#chunk_006, doc_system#chunk_001, doc_anorthite#chunk_002, doc_olivine#chunk_002, doc_spectroscopy#chunk_003, doc_system#chunk_007, doc_muscovite#chunk_002, doc_kaolinite#chunk_002, doc_system#chunk_009, doc_magnetite#chunk_002
category: reranker_demoted_gold
suspected_cause: reranker 或 rerank 特征把已召回的 gold evidence 排到了 top-k 之外。
next_action: 检查 reranker 输入候选、分数和 top-k；真实 reranker 消融时重点复核这类样例。
```
