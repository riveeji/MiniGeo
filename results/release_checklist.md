# MiniGeo 发布验收清单

本文件由 `scripts/write_release_checklist.py` 生成，用于检查最终展示材料是否齐全。当前仓库已按展示版封档，A100 final smoke 结果已经接入本地 `results/`。

## 汇总

- ready_items=10
- incomplete_items=0
- missing_items=0

## 交付项

| 交付项 | 状态 | 文件 | 缺失关键词 | 说明 |
|---|---|---|---|---|
| README | ready | README.md |  | 项目入口和复现实验说明 |
| 架构文档 | ready | docs/architecture.md |  | 系统分层和公共接口 |
| Benchmark 文档 | ready | docs/benchmark.md |  | 评测集规则和泄漏控制 |
| Data card | ready | docs/data-card.md |  | 语料、SFT 和版权说明 |
| 主结果表 | ready | results/main_results.md |  | 核心定量结果 |
| 失败案例分析 | ready | results/failure_cases.md |  | 可复查失败样例 |
| Agent 多案例报告 | ready | results/agent_cases.md |  | 混合文档和 SQL demo |
| Colab notebook 模板 | ready | notebooks/minigeo_colab_template.ipynb |  | Colab 入口 |
| A100 SFT runbook | ready | docs/a100-json-sft-smoke-cells.md |  | 封档后复现实验指令 |
| A100 evidence eval runbook | ready | docs/a100-json64-evidence-eval-cells.md |  | 封档后证据注入复现实验指令 |

## 封档后续策略

- 展示版已封档，不再安排 A100 或长训。
- 保留已完成的 json64 evidence final smoke 结果；后续只有在专门修复 malformed JSON 时才考虑重新开短 smoke。
- 继续保持 `reference_answer_leaks=[]`，adapter/checkpoints 不进 git。

## 本地下一步

本地展示材料已齐，展示版可以保持冻结状态。
