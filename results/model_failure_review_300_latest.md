# MiniGeo 失败样例人工抽检表

本文件用于人工判断 citation miss 的真实原因。CSV 中的 `review_decision` 建议只填写下列值之一：

- `model_error`：模型引用错误，gold evidence 正确。
- `label_expand`：模型引用的 chunk 也能支撑答案，应扩充 benchmark evidence label。
- `retrieval_error`：检索结果缺少必要证据，应改检索或语料。
- `ambiguous`：题目、答案或证据边界不清，需要重写样例。

## 分类数量

| Category | Count |
|---|---:|
| model_cited_neighbor | 26 |
| model_cited_other | 22 |

## 抽检样例

| ID | Category | Question | Gold | Citations |
|---|---|---|---|---|
| minigeo_027 | model_cited_other | 为什么开放资料需要记录 URL 和 license？ | doc_system#chunk_002 | doc_pyrite#chunk_002 |
| minigeo_030 | model_cited_other | 为什么说 MiniGeo 的贡献不是模型规模？ | doc_system#chunk_004 | doc_calcite#chunk_001 |
| minigeo_038 | model_cited_other | 为什么需要 failure case analysis？ | doc_system#chunk_005 | doc_pyrite#chunk_002 |
| minigeo_048 | model_cited_other | 能否声称 MiniGeo 已经训练出新的地学基础模型？ | doc_system#chunk_004 | doc_spectroscopy#chunk_003 |
| minigeo_049 | model_cited_other | 混合检索相比单一 BM25 的预期优势是什么？ | doc_system#chunk_009 | doc_pyrite#chunk_002 |
| minigeo_050 | model_cited_other | 为什么最终报告要包含 latency？ | doc_system#chunk_010 | doc_magnetite#chunk_002 |
| minigeo_053 | model_cited_neighbor | 识别石英时为什么需要证据来源？ | doc_quartz#chunk_001 | doc_quartz#chunk_002 |
| minigeo_055 | model_cited_other | 长石的常用组成或化学式是什么？ | doc_feldspar#chunk_001 | doc_anorthite#chunk_001 |
| minigeo_056 | model_cited_other | 识别长石时为什么需要证据来源？ | doc_feldspar#chunk_001 | doc_anorthite#chunk_002, doc_olivine#chunk_002 |
| minigeo_062 | model_cited_neighbor | 识别赤铁矿时为什么需要证据来源？ | doc_hematite#chunk_001 | doc_hematite#chunk_002, doc_magnetite#chunk_002 |
| minigeo_065 | model_cited_neighbor | 识别白云石时为什么需要证据来源？ | doc_dolomite#chunk_001 | doc_dolomite#chunk_002, doc_muscovite#chunk_002 |
| minigeo_071 | model_cited_neighbor | 识别磁铁矿时为什么需要证据来源？ | doc_magnetite#chunk_001 | doc_magnetite#chunk_002 |
| minigeo_074 | model_cited_neighbor | 识别黄铁矿时为什么需要证据来源？ | doc_pyrite#chunk_001 | doc_pyrite#chunk_002 |
| minigeo_077 | model_cited_neighbor | 识别橄榄石时为什么需要证据来源？ | doc_olivine#chunk_001 | doc_olivine#chunk_002 |
| minigeo_080 | model_cited_neighbor | 识别白云母时为什么需要证据来源？ | doc_muscovite#chunk_001 | doc_muscovite#chunk_002 |
| minigeo_083 | model_cited_other | 识别高岭石时为什么需要证据来源？ | doc_kaolinite#chunk_001 | doc_muscovite#chunk_002 |
| minigeo_086 | model_cited_neighbor | 识别钙长石时为什么需要证据来源？ | doc_anorthite#chunk_001 | doc_anorthite#chunk_002, doc_muscovite#chunk_002 |
| minigeo_131 | model_cited_neighbor | 比较赤铁矿和磁铁矿时为什么需要多条证据？ | doc_hematite#chunk_001, doc_magnetite#chunk_001 | doc_hematite#chunk_002, doc_magnetite#chunk_002 |
| minigeo_134 | model_cited_neighbor | 比较橄榄石和长石时为什么需要多条证据？ | doc_feldspar#chunk_001, doc_olivine#chunk_001 | doc_anorthite#chunk_002, doc_feldspar#chunk_002, doc_olivine#chunk_002 |
| minigeo_135 | model_cited_other | MiniGeo 如何避免在回答石英问题时产生无证据结论？ | doc_quartz#chunk_001 | doc_muscovite#chunk_002 |

## 使用方法

1. 打开配套 CSV，逐行检查 `answer` 是否被 `citations` 支撑。
2. 如果引用 chunk 可以支撑答案，在 `review_decision` 填 `label_expand`，并把应加入的 chunk 写入 `suggested_evidence`。
3. 如果引用 chunk 不能支撑答案，在 `review_decision` 填 `model_error`。
4. 如果 gold 没进 `retrieved_evidence`，优先填 `retrieval_error`。
