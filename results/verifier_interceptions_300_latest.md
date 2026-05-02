# MiniGeo Verifier 拦截样例

本文件用于人工判断 Verifier 拦截是否合理。CSV 中的 `review_decision` 建议只填写下列值之一：

- `correct_reject`：Verifier 正确拦截，原始回答确实未被证据充分支持。
- `false_reject`：Verifier 误杀，原始回答其实被证据支持。
- `claim_split_error`：claim 抽取过碎或抽错，导致误判。
- `needs_model_verifier`：本地 heuristic 不够，需要模型辅助 Verifier 复判。

## Verdict 数量

| Verdict | Count |
|---|---:|
| insufficient_evidence | 3 |
| partially_supported | 2 |

## 拦截样例

| ID | Verdict | Question | Unsupported Claims |
|---|---|---|---|
| minigeo_037 | insufficient_evidence | 资料库是否证明所有秦皇岛长石预测都是错误的？ | 资料库未证明所有秦皇岛长石预测都是错误的，现有证据仅涉及长石的一般定义、分类及光谱特征，未包含秦皇岛地区的具体预测数据或验证结果 |
| minigeo_059 | insufficient_evidence | 识别方解石时为什么需要证据来源？ | 识别方解石时需要证据来源，以便验证其作为碳酸盐矿物的分类（区别于硅酸盐矿物）以及与其他碳酸盐矿物（如含镁的白云石）或硬度更高的矿物（如石英）的性质差异，确保结论的准确性和可追溯性 |
| minigeo_131 | partially_supported | 比较赤铁矿和磁铁矿时为什么需要多条证据？ | 同时，两者均为铁氧化物矿物，需通过多种特征（如磁性、光谱特征）综合确认以避免误判 |
| minigeo_159 | insufficient_evidence | 识别方解石时为什么需要证据来源？ | 识别方解石时需要证据来源，以便验证其作为碳酸盐矿物的分类（区别于硅酸盐矿物）以及与其他碳酸盐矿物（如含镁的白云石）或硬度更高的矿物（如石英）的性质差异，确保结论的准确性和可追溯性 |
| minigeo_231 | partially_supported | 比较赤铁矿和磁铁矿时为什么需要多条证据？ | 同时，两者均为铁氧化物矿物，需通过多种特征（如磁性、光谱特征）综合确认以避免误判 |

## 使用方法

1. 对照 `unverified_answer`、`unsupported_claims` 和 `retrieved_evidence`。
2. 如果原始回答确实没有充分证据，填 `correct_reject`。
3. 如果证据其实支持原始回答，填 `false_reject` 或 `claim_split_error`。
4. 如果规则 Verifier 难以判断，填 `needs_model_verifier`，后续在 A100 上用模型辅助 Verifier 复判。
