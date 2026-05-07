# MiniGeo 发布验收清单

本文件由 `scripts/write_release_checklist.py` 生成，用于检查最终展示材料是否齐全。它只检查本地文件和关键文本，不代表外部 A100 结果已经重新跑完。

## 汇总

- ready_items=10
- incomplete_items=0
- missing_items=0

## 交付项

| 交付项 | 状态 | 文件 | 缺失关键词 | 说明 |
|---|---|---|---|---|
| README | ready | README.md |  | 项目入口和复现实验说明 |
| 架构文档 | ready | docs\architecture.md |  | 系统分层和公共接口 |
| Benchmark 文档 | ready | docs\benchmark.md |  | 评测集规则和泄漏控制 |
| Data card | ready | docs\data-card.md |  | 语料、SFT 和版权说明 |
| 主结果表 | ready | results\main_results.md |  | 核心定量结果 |
| 失败案例分析 | ready | results\failure_cases.md |  | 可复查失败样例 |
| Agent 多案例报告 | ready | results\agent_cases.md |  | 混合文档和 SQL demo |
| Colab notebook 模板 | ready | notebooks\minigeo_colab_template.ipynb |  | Colab 入口 |
| A100 SFT runbook | ready | docs\a100-json-sft-smoke-cells.md |  | 下一次 GPU smoke 指令 |
| A100 evidence eval runbook | ready | docs\a100-json64-evidence-eval-cells.md |  | 证据注入评测指令 |

## 剩余 GPU 任务

- 只在必要时开 A100，先运行 json64 evidence adapter 的短 smoke，确认原始尾部污染是否减少。
- 如果短 smoke 同时保持 citation/refusal 指标且原始输出格式稳定，再考虑 553step 或 1 epoch 小规模 SFT。
- 长训前继续保持 `reference_answer_leaks=[]`，adapter/checkpoints 不进 git。

## 本地下一步

本地展示材料已齐，可以进入最终人工通读和必要的 A100 短验证。
