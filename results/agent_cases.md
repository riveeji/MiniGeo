# MiniGeo-Agent 多案例本地评测

## 摘要

- 样例数：3
- 通过率：100.00%
- Planner 模式准确率：100.00%
- SQL 成功率：100.00%
- Verification report 覆盖率：100.00%
- 平均延迟：33.02 ms/case

## 案例明细

| case_id | 期望模式 | 实际模式 | 通过 | SQL 错误 | Evidence | Verdict |
|---|---|---|---:|---|---:|---|
| agent_hybrid_qhd_misclassification | hybrid | hybrid | 是 |  | 3 | supported |
| agent_sql_region_errors | sql | sql | 是 |  | 1 | supported |
| agent_docs_quartz_spectrum | docs | docs | 是 |  | 3 | supported |

## 问题与回答

### agent_hybrid_qhd_misclassification

- 问题：Analyze which mineral categories are most frequently misclassified in samples collected from Qinhuangdao, and explain possible causes using spectral evidence.
- 回答：SQL 结果显示，秦皇岛样本中最常被误判为 feldspar，误判分布为 feldspar（2 次）, quartz（1 次）。可能原因包括：石英的 464 cm-1 附近拉曼峰是关键识别证据，长石与石英同属硅酸盐体系，Al-Si 骨架相关光谱特征可能增加混淆风险。相关证据见 [doc_feldspar#chunk_002] [doc_quartz#chunk_002]。

### agent_sql_region_errors

- 问题：每个地区有多少错误预测？
- 回答：SQL 查询返回 1 行结果：region=Qinhuangdao, errors=3。

### agent_docs_quartz_spectrum

- 问题：石英的主要拉曼光谱证据是什么？
- 回答：根据文档证据，石英常见强拉曼峰接近 464 cm-1，可作为识别石英的重要光谱证据。相关证据见 [doc_quartz#chunk_002]。
