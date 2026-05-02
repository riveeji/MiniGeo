# MiniGeo Verifier 拦截样例

本文件用于人工判断 Verifier 拦截是否合理。CSV 中的 `review_decision` 建议只填写下列值之一：

- `correct_reject`：Verifier 正确拦截，原始回答确实未被证据充分支持。
- `false_reject`：Verifier 误杀，原始回答其实被证据支持。
- `claim_split_error`：claim 抽取过碎或抽错，导致误判。
- `needs_model_verifier`：本地 heuristic 不够，需要模型辅助 Verifier 复判。

## Verdict 数量

| Verdict | Count |
|---|---:|
| insufficient_evidence | 2 |

## 拦截样例

| ID | Verdict | Question | Unsupported Claims |
|---|---|---|---|
| minigeo_037 | insufficient_evidence | 资料库是否证明所有秦皇岛长石预测都是错误的？ | 资料库未证明所有秦皇岛长石预测都是错误的 |
| minigeo_039 | insufficient_evidence | MiniGeo 是否应该在没有证据时回答陨石样本的年龄？ | MiniGeo 不应在没有证据时回答陨石样本的年龄，因为证据验证机制要求 claim 必须有支持证据，否则应标记为 insufficient_evidence |

## 使用方法

1. 对照 `unverified_answer`、`unsupported_claims` 和 `retrieved_evidence`。
2. 如果原始回答确实没有充分证据，填 `correct_reject`。
3. 如果证据其实支持原始回答，填 `false_reject` 或 `claim_split_error`。
4. 如果规则 Verifier 难以判断，填 `needs_model_verifier`，后续在 A100 上用模型辅助 Verifier 复判。
