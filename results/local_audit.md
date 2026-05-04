# MiniGeo 本地总验收报告

本报告由 `scripts/audit_project.py` 生成，用于记录当前仓库在本地环境中可复现的基础验收结果。

## 总览

| 步骤 | 状态 | 退出码 | 命令 |
|---|---|---:|---|
| 单元测试 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe -m pytest -q --basetemp .pytest_tmp\basetemp-584 -p no:cacheprovider` |
| Benchmark 分布 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/evaluate_bench.py` |
| 检索消融 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/evaluate_retrieval_ablation.py` |
| 检索失败分析 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/analyze_retrieval_failures.py` |
| 拒答评测 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/evaluate_abstention.py` |
| Verifier 评测 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/evaluate_verifier.py` |
| SQL 评测 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/evaluate_sql.py` |
| Agent Planner 评测 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/evaluate_agent_planner.py` |
| SFT 数据构建 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/build_sft_corpus.py` |
| 数据质量审计 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/audit_data_quality.py` |
| QLoRA 配置检查 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/train_lora.py --check-only` |
| Agent Demo | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/agent_demo.py` |
| 结果文档生成 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/write_report_artifacts.py` |
| 本地结果摘要 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/write_local_results.py` |

## 详细输出

### 单元测试

- 状态：PASS
- 退出码：0

**stdout**

```text
........................................................................ [ 51%]
...................................................................      [100%]
139 passed in 2.92s
```

### Benchmark 分布

- 状态：PASS
- 退出码：0

**stdout**

```text
items=300
types={'concept': 33, 'false_premise': 39, 'evidence': 63, 'spectroscopy': 13, 'unanswerable': 33, 'sql': 57, 'mineral_property': 39, 'multi_hop': 23}
difficulty={'easy': 90, 'medium': 210}
answerable=267
unanswerable=33
requires_sql=60
evidence_labeled=209
```

### 检索消融

- 状态：PASS
- 退出码：0

**stdout**

```text
bm25: recall@5=0.976 recall@10=1.000 mrr=0.774 citation_hit_rate=1.000 latency_ms=3.943
dense: recall@5=0.550 recall@10=0.828 mrr=0.393 citation_hit_rate=0.828 latency_ms=1.886
hybrid: recall@5=0.914 recall@10=0.995 mrr=0.636 citation_hit_rate=0.995 latency_ms=5.715
hybrid_rerank: recall@5=0.608 recall@10=0.880 mrr=0.476 citation_hit_rate=0.880 latency_ms=19.488
```

### 检索失败分析

- 状态：PASS
- 退出码：0

**stdout**

```text
wrote=results\retrieval_failure_analysis.md
wrote=results\retrieval_failure_analysis.csv
```

### 拒答评测

- 状态：PASS
- 退出码：0

**stdout**

```text
items=300
abstention_accuracy=1.0
correct_abstain=33
missed_abstain=0
false_abstain=0
correct_answer=267
latency_ms=31.44900266668022
```

### Verifier 评测

- 状态：PASS
- 退出码：0

**stdout**

```text
reports=300
claims=314
verdicts={'supported': 113, 'insufficient_evidence': 179, 'partially_supported': 8}
statuses={'supported': 122, 'insufficient': 192}
unsupported_claim_rate=0.6114649681528662
latency_ms=1.2153989999933401
```

### SQL 评测

- 状态：PASS
- 退出码：0

**stdout**

```text
sql_items=60
sql_exec_accuracy=1.0
failures={}
latency_ms=0.6196666667771448
```

### Agent Planner 评测

- 状态：PASS
- 退出码：0

**stdout**

```text
items=300
sql_routing_accuracy=1.0
modes={'docs': 240, 'hybrid': 3, 'sql': 57}
latency_ms=0.0038919999982075146
```

### SFT 数据构建

- 状态：PASS
- 退出码：0

**stdout**

```text
items=135
output=data\processed\sft_corpus.jsonl
reference_answer_leaks=[]
```

### 数据质量审计

- 状态：PASS
- 退出码：0

**stdout**

```text
benchmark_items=300
corpus_chunks=42
sft_items=135
missing_evidence_refs=[]
reference_answer_leaks=[]
metadata_missing=[]
placeholder_source_urls=[]
duplicate_chunk_ids=[]
duplicate_benchmark_ids=[]
duplicate_sft_ids=[]
```

### QLoRA 配置检查

- 状态：PASS
- 退出码：0

**stdout**

```text
QLoRA config check passed.
base_model=Qwen/Qwen3.5-2B
train_path=data/processed/sft_corpus.jsonl
eval_path=data/benchmark/minigeo_bench.jsonl
output_dir=checkpoints/MiniGeo-Qwen3.5-2B-SFT
```

### Agent Demo

- 状态：PASS
- 退出码：0

**stdout**

```text
{
  "answer": "SQL �����ʾ���ػʵ��������������Ϊ feldspar�����зֲ�Ϊ feldspar��2 �Σ�, quartz��1 �Σ�������ԭ�������ʯӢ�� 464 cm-1 �����������ǹؼ�ʶ��֤�ݣ���ʯ��ʯӢͬ����������ϵ��Al-Si �Ǽ���ع��������������ӻ������ա����֤�ݼ� [doc_feldspar#chunk_002] [doc_quartz#chunk_002]��",
  "sql": "select predictions.predicted_mineral, count(*) as errors from predictions join samples on samples.sample_id = predictions.sample_id where samples.region = 'Qinhuangdao' and predictions.is_correct = 0 group by predicted_mineral order by errors desc",
  "evidence": [
    "agent_sql#result",
    "doc_feldspar#chunk_002",
    "doc_quartz#chunk_002"
  ],
  "verification": {
    "verdict": "supported",
    "claims": [
      {
        "claim": "SQL �����ʾ���ػʵ��������������Ϊ feldspar�����зֲ�Ϊ feldspar��2 �Σ�, quartz��1 �Σ�",
        "status": "supported",
        "evidence": [
          "agent_sql#result"
        ],
        "confidence": 1.0
      },
      {
        "claim": "����ԭ�������ʯӢ�� 464 cm-1 �����������ǹؼ�ʶ��֤�ݣ���ʯ��ʯӢͬ����������ϵ��Al-Si �Ǽ���ع��������������ӻ�������",
        "status": "supported",
        "evidence": [
          "doc_feldspar#chunk_002",
          "doc_quartz#chunk_002"
        ],
        "confidence": 0.4574468085106383
      },
      {
        "claim": "���֤�ݼ� [doc_feldspar#chunk_002] [doc_quartz#chunk_002]",
        "status": "supported",
        "evidence": [
          "doc_quartz#chunk_002"
        ],
        "confidence": 0.3076923076923077
      }
    ]
  },
  "limitations": [
    "��ǰ Agent ʹ����ʾ���ݿ���������ϣ�����ֻ������֤��������",
    "����ԭ�����Լ���֤�ݺ͹����ֶεĽ����Թ��ɣ���Ҫ��ʵʵ���¼���ˡ�"
  ],
  "sql_result": {
    "sql": "select predictions.predicted_mineral, count(*) as errors from predictions join samples on samples.sample_id = predictions.sample_id where samples.region = 'Qinhuangdao' and predictions.is_correct = 0 group by predicted_mineral order by errors desc",
    "execution_result": [
      {
        "predicted_mineral": "feldspar",
        "errors": 2
      },
      {
        "predicted_mineral": "quartz",
        "errors": 1
      }
    ],
    "error": null
  },
  "plan": {
    "mode": "hybrid",
    "requires_sql": true,
    "requires_docs": true,
    "requires_verification": true,
    "tools": [
      "generate_sql",
      "execute_sql",
      "retrieve_evidence",
      "verify_answer",
      "write_report"
    ]
  }
}
```

### 结果文档生成

- 状态：PASS
- 退出码：0

**stdout**

```text
wrote=results/main_results.md
wrote=results/failure_cases.md
```

### 本地结果摘要

- 状态：PASS
- 退出码：0

**stdout**

```text
wrote=results\local_eval_summary.md
```
