# MiniGeo Verifier 评测

当前评测使用本地启发式 Verifier，对 `data/benchmark/minigeo_bench.jsonl` 的 reference answer 和 gold evidence 进行验证。

运行：

```powershell
$env:PYTHONPATH="src"
python scripts/evaluate_verifier.py
```

当前结果：

```text
reports=150
claims=167
verdicts={'supported': 70, 'insufficient_evidence': 79, 'partially_supported': 1}
statuses={'supported': 74, 'insufficient': 93}
unsupported_claim_rate=0.5568862275449101
```

说明：

- 当前版本偏保守，许多 reference answer 因 token overlap 不足被标为 `insufficient`。
- 下一步应接入模型辅助 support classifier，比较启发式和模型版 Verifier。

