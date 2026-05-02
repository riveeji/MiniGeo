# MiniGeo 本地评测汇总

本文件由 `scripts/write_local_results.py` 生成，记录当前本地 baseline 的可复现实验结果。

## Benchmark

- 题目数：300
- SQL 题数：60
- 带 evidence label：209

## Retrieval

| 系统 | Recall@5 | Recall@10 | MRR | Citation Hit |
|---|---:|---:|---:|---:|
| bm25 | 0.976 | 1.000 | 0.774 | 1.000 |
| dense | 0.550 | 0.828 | 0.393 | 0.828 |
| hybrid | 0.914 | 0.995 | 0.636 | 0.995 |
| hybrid_rerank | 0.608 | 0.880 | 0.476 | 0.880 |

## Verifier

- reports：300
- claims：314
- unsupported_claim_rate：0.611

## SQL

- sql_items：60
- sql_exec_accuracy：1.000
- failures：{}
