# MiniGeo 本地评测汇总

本文件由 `scripts/write_local_results.py` 生成，记录当前本地 baseline 的可复现实验结果。

## Benchmark

- 题目数：300
- SQL 题数：60
- 带 evidence label：209

## Retrieval

| 系统 | Recall@5 | Recall@10 | MRR | Citation Hit |
|---|---:|---:|---:|---:|
| bm25 | 0.756 | 0.943 | 0.523 | 0.943 |
| dense | 0.550 | 0.828 | 0.393 | 0.828 |
| hybrid | 0.703 | 0.895 | 0.472 | 0.895 |
| hybrid_rerank | 0.589 | 0.833 | 0.452 | 0.833 |

## Verifier

- reports：300
- claims：343
- unsupported_claim_rate：0.638

## SQL

- sql_items：60
- sql_exec_accuracy：1.000
- failures：{}
