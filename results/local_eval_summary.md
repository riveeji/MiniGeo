# MiniGeo 本地评测汇总

本文件由 `scripts/write_local_results.py` 生成，记录当前本地 baseline 的可复现实验结果。

## Benchmark

- 题目数：150
- SQL 题数：30
- 带 evidence label：105

## Retrieval

| 系统 | Recall@5 | Recall@10 | MRR | Citation Hit |
|---|---:|---:|---:|---:|
| bm25 | 0.743 | 0.924 | 0.575 | 0.924 |
| dense | 0.600 | 0.819 | 0.440 | 0.819 |
| hybrid | 0.695 | 0.876 | 0.517 | 0.876 |
| hybrid_rerank | 0.600 | 0.838 | 0.524 | 0.838 |

## Verifier

- reports：150
- claims：167
- unsupported_claim_rate：0.557

## SQL

- sql_items：30
- sql_exec_accuracy：1.000
- failures：{}
