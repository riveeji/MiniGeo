# MiniGeo 风险与控制

| 风险 | 控制方式 |
|---|---|
| 中文文本编码损坏 | 所有文本按 UTF-8 读写；测试中保留中文样例。 |
| 中文 BM25 效果弱 | 优先使用 `jieba`，无依赖时回退到字符 bigram；后续和 dense retrieval 对比。 |
| Benchmark 泄漏 | 不使用 MiniGeo-Bench reference answer 作为训练输出。 |
| 数据版权不清 | 提交元数据和处理脚本，不提交版权不明确的原始文件。 |
| Colab 显存不足 | 默认使用 Qwen3.5-2B，QLoRA 先跑 smoke test。 |
| Verifier 误判 | 在 `results/failure_cases.md` 记录人工复核失败案例。 |
| Agent prompt 不稳定 | 先单独测试 SQL 工具，再组合文档检索和 SQL Agent。 |

