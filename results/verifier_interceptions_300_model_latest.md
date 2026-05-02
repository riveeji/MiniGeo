# MiniGeo Verifier 拦截样例

本文件用于人工判断 Verifier 拦截是否合理。CSV 中的 `review_decision` 建议只填写下列值之一：

- `correct_reject`：Verifier 正确拦截，原始回答确实未被证据充分支持。
- `false_reject`：Verifier 误杀，原始回答其实被证据支持。
- `claim_split_error`：claim 抽取过碎或抽错，导致误判。
- `needs_model_verifier`：本地 heuristic 不够，需要模型辅助 Verifier 复判。

## Verdict 数量

| Verdict | Count |
|---|---:|
| contradicted | 2 |
| insufficient_evidence | 4 |
| partially_supported | 1 |

## 拦截样例

| ID | Verdict | Question | Unsupported Claims |
|---|---|---|---|
| minigeo_002 | contradicted | 石英和长石都属于哪一大类矿物？ | 石英和长石都属于硅酸盐矿物 |
| minigeo_028 | contradicted | Benchmark reference answer 可以直接作为 SFT 输出训练吗？ | 直接作为 SFT 输出训练会降低 benchmark 泄漏风险。 |
| minigeo_035 | partially_supported | 如果 SQL 执行失败，Agent 应该直接放弃吗？ | 否，Agent 不应直接放弃 |
| minigeo_037 | insufficient_evidence | 资料库是否证明所有秦皇岛长石预测都是错误的？ | 资料库未证明所有秦皇岛长石预测都是错误的，现有证据仅涉及长石的一般定义、分类及光谱特征，未包含秦皇岛地区的具体预测数据或验证结果 |
| minigeo_061 | insufficient_evidence | 赤铁矿的常用组成或化学式是什么？ | 赤铁矿是铁氧化物矿物，其常用化学式为 Fe2O3 |
| minigeo_161 | insufficient_evidence | 赤铁矿的常用组成或化学式是什么？ | 赤铁矿是铁氧化物矿物，其常用化学式为 Fe2O3 |
| minigeo_277 | insufficient_evidence | 比较磁铁矿和白云母类别时需要哪些证据？ | 比较磁铁矿和白云母类别时，需要利用磁铁矿的磁性特征（如 Fe3O4 化学式）和白云母的片状解理特征，并结合结构或光谱证据进行最终确认 |

## 使用方法

1. 对照 `unverified_answer`、`unsupported_claims` 和 `retrieved_evidence`。
2. 如果原始回答确实没有充分证据，填 `correct_reject`。
3. 如果证据其实支持原始回答，填 `false_reject` 或 `claim_split_error`。
4. 如果规则 Verifier 难以判断，填 `needs_model_verifier`，后续在 A100 上用模型辅助 Verifier 复判。
