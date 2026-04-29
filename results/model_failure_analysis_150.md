# MiniGeo 模型失败分析

本报告基于已保存的 Qwen3.5-4B + BM25 RAG 输出离线生成，不会再次调用模型。

- total_records：150
- citation_misses：35
- citation_miss_rate：0.233

## 分类统计

| Category | Count |
|---|---:|
| model_abstained_with_gold | 5 |
| model_cited_neighbor | 10 |
| model_cited_other | 18 |
| retrieval_gold_missing | 2 |

## 样例

```text
id: minigeo_021
category: model_abstained_with_gold
question: 秦皇岛错误预测样本的可能光谱原因是什么？
gold: doc_feldspar#chunk_002, doc_quartz#chunk_002, doc_spectroscopy#chunk_003
citations: None
retrieved: doc_system#chunk_005, doc_hematite#chunk_002, doc_spectroscopy#chunk_004, doc_quartz#chunk_002, doc_system#chunk_010
answer: 证据不足
```

```text
id: minigeo_053
category: model_cited_neighbor
question: 识别石英时为什么需要证据来源？
gold: doc_quartz#chunk_001
citations: doc_quartz#chunk_002, doc_system#chunk_001
retrieved: doc_muscovite#chunk_002, doc_system#chunk_001, doc_quartz#chunk_001, doc_quartz#chunk_002, doc_system#chunk_006
answer: 识别石英时需要证据来源，因为可信的回答需要可追踪的证据来支持结论，例如石英的强拉曼峰接近464 cm-1可作为重要光谱证据，同时返回证据来源便于检查引用是否支持结论。
```

```text
id: minigeo_055
category: model_cited_other
question: 长石的常用组成或化学式是什么？
gold: doc_feldspar#chunk_001
citations: doc_anorthite#chunk_001
retrieved: doc_feldspar#chunk_001, doc_anorthite#chunk_001, doc_gypsum#chunk_001, doc_dolomite#chunk_001, doc_feldspar#chunk_002
answer: 长石的化学组成可表示为 CaAl2Si2O8（以钙长石为例）。
```

```text
id: minigeo_056
category: model_cited_other
question: 识别长石时为什么需要证据来源？
gold: doc_feldspar#chunk_001
citations: doc_muscovite#chunk_002, doc_system#chunk_001
retrieved: doc_feldspar#chunk_001, doc_muscovite#chunk_002, doc_system#chunk_001, doc_anorthite#chunk_002, doc_olivine#chunk_002
answer: 识别长石时需要证据来源，因为可信回答需要证据来源支持，且RAG回答返回chunk id可以让答案证据来源可追踪，便于检查引用是否支持结论。
```

```text
id: minigeo_058
category: model_abstained_with_gold
question: 方解石的常用组成或化学式是什么？
gold: doc_calcite#chunk_001
citations: None
retrieved: doc_calcite#chunk_001, doc_calcite#chunk_002, doc_dolomite#chunk_001, doc_quartz#chunk_003, doc_dolomite#chunk_002
answer: 方解石的化学式为 CaCO3
```

```text
id: minigeo_059
category: model_cited_other
question: 识别方解石时为什么需要证据来源？
gold: doc_calcite#chunk_001
citations: doc_system#chunk_001
retrieved: doc_muscovite#chunk_002, doc_system#chunk_001, doc_calcite#chunk_001, doc_dolomite#chunk_002, doc_quartz#chunk_003
answer: 识别方解石时需要证据来源，以便让答案的可追踪性增强，便于检查引用是否支持结论。
```

```text
id: minigeo_062
category: model_cited_neighbor
question: 识别赤铁矿时为什么需要证据来源？
gold: doc_hematite#chunk_001
citations: doc_hematite#chunk_002, doc_magnetite#chunk_002, doc_system#chunk_001
retrieved: doc_muscovite#chunk_002, doc_hematite#chunk_002, doc_system#chunk_001, doc_hematite#chunk_001, doc_magnetite#chunk_002
answer: 识别赤铁矿时需要证据来源，因为最终结论应结合结构或光谱证据，仅凭单一特征（如磁性）不足以区分赤铁矿与其他矿物（如磁铁矿），且可信回答需可追踪引用以支持结论。
```

```text
id: minigeo_065
category: model_cited_other
question: 识别白云石时为什么需要证据来源？
gold: doc_dolomite#chunk_001
citations: doc_system#chunk_001, doc_system#chunk_006
retrieved: doc_muscovite#chunk_002, doc_dolomite#chunk_001, doc_system#chunk_001, doc_dolomite#chunk_002, doc_system#chunk_006
answer: 识别白云石时需要证据来源，以便让答案的可追踪性提高，便于检查引用是否支持结论，从而提高地学解释的可信度。
```

```text
id: minigeo_068
category: model_cited_other
question: 识别石膏时为什么需要证据来源？
gold: doc_gypsum#chunk_001
citations: doc_system#chunk_001, doc_system#chunk_006
retrieved: doc_muscovite#chunk_002, doc_gypsum#chunk_001, doc_system#chunk_001, doc_quartz#chunk_002, doc_system#chunk_006
answer: 识别石膏时需要证据来源，因为提供证据来源可以让答案的可追踪性提高，便于检查引用是否支持结论，从而提高地学解释的可信度。
```

```text
id: minigeo_071
category: model_cited_neighbor
question: 识别磁铁矿时为什么需要证据来源？
gold: doc_magnetite#chunk_001
citations: doc_magnetite#chunk_002
retrieved: doc_muscovite#chunk_002, doc_magnetite#chunk_001, doc_magnetite#chunk_002, doc_system#chunk_001, doc_hematite#chunk_002
answer: 识别磁铁矿时需要证据来源，因为虽然磁性可以辅助区分磁铁矿和赤铁矿，但最终结论仍应结合结构或光谱证据，以确保回答的可信度和准确性。
```

```text
id: minigeo_074
category: model_cited_neighbor
question: 识别黄铁矿时为什么需要证据来源？
gold: doc_pyrite#chunk_001
citations: doc_pyrite#chunk_002, doc_system#chunk_001, doc_system#chunk_006
retrieved: doc_muscovite#chunk_002, doc_pyrite#chunk_002, doc_pyrite#chunk_001, doc_system#chunk_001, doc_system#chunk_006
answer: 识别黄铁矿时需要证据来源，因为仅凭金属光泽无法单独证明其为金或氧化物，必须结合硬度、条痕和成分等证据进行综合判断，以确保结论的准确性和可追踪性。
```

```text
id: minigeo_076
category: model_abstained_with_gold
question: 橄榄石的常用组成或化学式是什么？
gold: doc_olivine#chunk_001
citations: None
retrieved: doc_olivine#chunk_001, doc_olivine#chunk_002, doc_dolomite#chunk_001, doc_gypsum#chunk_001, doc_magnetite#chunk_001
answer: 证据不足
```

## 下一步处理建议

1. 先处理 `model_cited_other`：gold chunk 已在 prompt 中但模型引用了其他 chunk，优先收紧 citation prompt，并在 Verifier 中检查最终引用是否逐条支撑回答。
2. 再处理 `model_cited_neighbor`：这类多半是 chunk 粒度或 gold label 过窄，适合人工抽检后决定是否扩充 evidence label。
3. 单独处理 `model_abstained_with_gold`：gold evidence 已进入 prompt 仍拒答，说明拒答阈值或 JSON 解析后的 abstained 字段需要调参。
4. 最后处理 `retrieval_gold_missing`：数量少但是真检索问题，应补 query expansion、reranker 或 corpus 覆盖。

## 分类解释

- `retrieval_gold_missing`：gold evidence 没有进入 RAG prompt，主要应改检索或 evidence label。
- `model_abstained_with_gold`：gold evidence 已进入 prompt，但模型仍拒答，主要应改 prompt 或拒答策略。
- `model_cited_neighbor`：模型引用了同一文档的相邻 chunk，可能是 gold label 过窄或 citation policy 不够严格。
- `model_cited_other`：模型引用了非 gold、非相邻 chunk，优先检查 reranker、prompt 和 benchmark 标注。
