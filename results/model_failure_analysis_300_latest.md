# MiniGeo 模型失败分析

本报告基于已保存的 Qwen3.5-4B + BM25 RAG 输出离线生成，不会再次调用模型。

- total_records：300
- citation_misses：65
- citation_miss_rate：0.217

## 分类统计

| Category | Count |
|---|---:|
| model_abstained_with_gold | 12 |
| model_cited_neighbor | 26 |
| model_cited_other | 22 |
| retrieval_gold_missing | 5 |

## 样例

```text
id: minigeo_021
category: model_abstained_with_gold
question: 秦皇岛错误预测样本的可能光谱原因是什么？
gold: doc_feldspar#chunk_002, doc_quartz#chunk_002, doc_spectroscopy#chunk_003
citations: None
retrieved: doc_system#chunk_005, doc_hematite#chunk_002, doc_spectroscopy#chunk_004, doc_quartz#chunk_002, doc_system#chunk_010
answer: 证据不足以确定秦皇岛错误预测样本的具体光谱原因，因为提供的材料仅包含通用系统说明、赤铁矿和石英的光谱特征描述以及拉曼光谱的一般影响因素，未提及秦皇岛样本的具体光谱数据或错误类型。
```

```text
id: minigeo_027
category: model_cited_other
question: 为什么开放资料需要记录 URL 和 license？
gold: doc_system#chunk_002
citations: doc_pyrite#chunk_002
retrieved: doc_system#chunk_002, doc_system#chunk_011, doc_pyrite#chunk_002, doc_dolomite#chunk_002, doc_olivine#chunk_002
answer: 开放资料需要记录 URL 和 license，以便控制来源追踪和版权风险。
```

```text
id: minigeo_030
category: model_cited_other
question: 为什么说 MiniGeo 的贡献不是模型规模？
gold: doc_system#chunk_004
citations: doc_calcite#chunk_001
retrieved: doc_system#chunk_004, doc_hematite#chunk_001, doc_calcite#chunk_001, doc_system#chunk_011, doc_system#chunk_012
answer: MiniGeo 的贡献在于构建 benchmark、RAG、证据验证和数据分析闭环，而非训练新的地学基础模型。
```

```text
id: minigeo_038
category: model_cited_other
question: 为什么需要 failure case analysis？
gold: doc_system#chunk_005
citations: doc_pyrite#chunk_002
retrieved: doc_system#chunk_005, doc_system#chunk_004, doc_system#chunk_011, doc_pyrite#chunk_002, doc_system#chunk_009
answer: 失败案例分析需要区分数据缺失、检索失败、生成错误、验证误判和 SQL 错误，以确保系统能够准确识别问题来源并改进性能。
```

```text
id: minigeo_048
category: model_cited_other
question: 能否声称 MiniGeo 已经训练出新的地学基础模型？
gold: doc_system#chunk_004
citations: doc_spectroscopy#chunk_003
retrieved: doc_system#chunk_004, doc_system#chunk_003, doc_spectroscopy#chunk_003, doc_system#chunk_006, doc_system#chunk_012
answer: 不能声称 MiniGeo 已经训练出新的地学基础模型，因为 MiniGeo 的贡献是 benchmark、RAG、证据验证和数据分析闭环，而不是训练新的地学基础模型。
```

```text
id: minigeo_049
category: model_cited_other
question: 混合检索相比单一 BM25 的预期优势是什么？
gold: doc_system#chunk_009
citations: doc_pyrite#chunk_002
retrieved: doc_system#chunk_009, doc_system#chunk_011, doc_system#chunk_005, doc_pyrite#chunk_002, doc_quartz#chunk_003
answer: 混合检索相比单一 BM25 的预期优势是具有更高的证据召回率，因为它结合了词项匹配和语义匹配。
```

```text
id: minigeo_050
category: model_cited_other
question: 为什么最终报告要包含 latency？
gold: doc_system#chunk_010
citations: doc_magnetite#chunk_002
retrieved: doc_magnetite#chunk_002, doc_system#chunk_006, doc_gypsum#chunk_001, doc_dolomite#chunk_002, doc_system#chunk_010
answer: 最终报告包含 latency 是因为它是系统可用性评估的一部分，用于反映端到端响应成本。
```

```text
id: minigeo_053
category: model_cited_neighbor
question: 识别石英时为什么需要证据来源？
gold: doc_quartz#chunk_001
citations: doc_quartz#chunk_002
retrieved: doc_muscovite#chunk_002, doc_system#chunk_001, doc_quartz#chunk_001, doc_quartz#chunk_002, doc_system#chunk_006
answer: 识别石英时需要证据来源，因为光谱证据（如强拉曼峰接近 464 cm-1）可作为识别石英的重要依据，且返回证据来源可追踪引用是否支持结论。
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
citations: doc_anorthite#chunk_002, doc_olivine#chunk_002
retrieved: doc_feldspar#chunk_001, doc_muscovite#chunk_002, doc_system#chunk_001, doc_anorthite#chunk_002, doc_olivine#chunk_002
answer: 识别长石时，需要证据来源以确保分类准确，避免将长石族矿物（如钙长石）误归为其他类别（如碳酸盐矿物），并需结合晶体结构和谱学证据进行区分。
```

```text
id: minigeo_058
category: model_abstained_with_gold
question: 方解石的常用组成或化学式是什么？
gold: doc_calcite#chunk_001
citations: None
retrieved: doc_calcite#chunk_001, doc_calcite#chunk_002, doc_dolomite#chunk_001, doc_quartz#chunk_003, doc_dolomite#chunk_002
answer: 方解石的化学式为 CaCO3。
```

```text
id: minigeo_062
category: model_cited_neighbor
question: 识别赤铁矿时为什么需要证据来源？
gold: doc_hematite#chunk_001
citations: doc_hematite#chunk_002, doc_magnetite#chunk_002
retrieved: doc_muscovite#chunk_002, doc_hematite#chunk_002, doc_system#chunk_001, doc_hematite#chunk_001, doc_magnetite#chunk_002
answer: 识别赤铁矿时需要证据来源，因为最终结论应结合结构或光谱证据，仅靠单一特征（如磁性）不足以区分赤铁矿与其他矿物（如磁铁矿）。
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
