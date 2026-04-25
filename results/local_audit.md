# MiniGeo 本地总验收报告

本报告由 `scripts/audit_project.py` 生成，用于记录当前仓库在本地环境中可复现的基础验收结果。

## 总览

| 步骤 | 状态 | 退出码 | 命令 |
|---|---|---:|---|
| 单元测试 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe -m pytest -q` |
| Benchmark 分布 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/evaluate_bench.py` |
| 检索消融 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/evaluate_retrieval_ablation.py` |
| Verifier 评测 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/evaluate_verifier.py` |
| SQL 评测 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/evaluate_sql.py` |
| SFT 数据构建 | PASS | 0 | `J:\MiniGeo\.venv\Scripts\python.exe scripts/build_sft_corpus.py` |
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
....................................................................     [100%]
68 passed in 0.26s
```

### Benchmark 分布

- 状态：PASS
- 退出码：0

**stdout**

```text
items=150
types={'concept': 21, 'false_premise': 19, 'evidence': 35, 'spectroscopy': 4, 'unanswerable': 17, 'sql': 27, 'mineral_property': 18, 'multi_hop': 9}
difficulty={'easy': 58, 'medium': 92}
answerable=133
unanswerable=17
requires_sql=30
evidence_labeled=105
```

### 检索消融

- 状态：PASS
- 退出码：0

**stdout**

```text
bm25: recall@5=0.743 recall@10=0.924 mrr=0.575 citation_hit_rate=0.924 latency_ms=0.561
dense: recall@5=0.600 recall@10=0.819 mrr=0.440 citation_hit_rate=0.819 latency_ms=1.311
hybrid: recall@5=0.695 recall@10=0.876 mrr=0.517 citation_hit_rate=0.876 latency_ms=30.024
hybrid_rerank: recall@5=0.600 recall@10=0.838 mrr=0.524 citation_hit_rate=0.838 latency_ms=36.277
```

### Verifier 评测

- 状态：PASS
- 退出码：0

**stdout**

```text
reports=150
claims=167
verdicts={'supported': 70, 'insufficient_evidence': 79, 'partially_supported': 1}
statuses={'supported': 74, 'insufficient': 93}
unsupported_claim_rate=0.5568862275449101
latency_ms=0.5721306666479601
```

### SQL 评测

- 状态：PASS
- 退出码：0

**stdout**

```text
sql_items=30
sql_exec_accuracy=1.0
failures={}
latency_ms=0.2224933333006144
```

### SFT 数据构建

- 状态：PASS
- 退出码：0

**stdout**

```text
items=89
output=data\processed\sft_corpus.jsonl
reference_answer_leaks=[]
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
    "doc_feldspar#chunk_002",
    "doc_quartz#chunk_002"
  ],
  "verification": {
    "verdict": "partially_supported",
    "claims": [
      {
        "claim": "SQL �����ʾ���ػʵ��������������Ϊ feldspar�����зֲ�Ϊ feldspar��2 �Σ�, quartz��1 �Σ�",
        "status": "insufficient",
        "evidence": [],
        "confidence": 0.0
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
