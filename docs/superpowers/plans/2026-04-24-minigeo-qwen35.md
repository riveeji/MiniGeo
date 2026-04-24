# MiniGeo Qwen3.5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build MiniGeo as a Qwen3.5-based geoscience trustworthy QA and data analysis agent system.

**Architecture:** The system uses Qwen3.5-2B as the main model, a hybrid RAG pipeline for geoscience evidence retrieval, a verifier for claim-level evidence checking, and an agent layer for SQL-backed analysis. Evaluation is centered on MiniGeo-Bench rather than subjective demos.

**Tech Stack:** Python, PyTorch, Transformers, PEFT, bitsandbytes, FAISS, BM25, pandas, FastAPI or Gradio, SQLite or PostgreSQL.

---

### Task 1: Initialize Project Skeleton

**Files:**
- Create: `requirements.txt`
- Create: `src/minigeo/__init__.py`
- Create: `src/minigeo/rag/__init__.py`
- Create: `src/minigeo/verifier/__init__.py`
- Create: `src/minigeo/eval/__init__.py`
- Create: `src/minigeo/agent/__init__.py`

- [ ] **Step 1: Create dependency file**

Create `requirements.txt` with:

```text
torch
transformers
accelerate
peft
bitsandbytes
datasets
sentence-transformers
faiss-cpu
rank-bm25
pandas
numpy
scikit-learn
tqdm
pyyaml
fastapi
uvicorn
gradio
pytest
```

- [ ] **Step 2: Create package marker files**

Create empty `__init__.py` files in each package directory listed above.

- [ ] **Step 3: Install dependencies**

Run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Expected: all dependencies install without import errors.

### Task 2: Create MiniGeo-Bench MVP

**Files:**
- Create: `data/benchmark/minigeo_bench.jsonl`
- Create: `scripts/evaluate_bench.py`

- [ ] **Step 1: Add first benchmark records**

Create `data/benchmark/minigeo_bench.jsonl` with at least these seed records:

```jsonl
{"id":"minigeo_001","question":"石英和长石在常见物理性质上有什么区别？","answer":"石英通常硬度较高，主要成分为二氧化硅；长石是一类铝硅酸盐矿物，常见于火成岩和变质岩中。","evidence":[],"type":"mineral_property","difficulty":"easy","answerable":true,"requires_sql":false}
{"id":"minigeo_002","question":"如果资料库中没有某个样本的光谱记录，系统应该如何回答？","answer":"系统应说明当前证据不足，不能给出确定结论，并提示需要补充光谱记录。","evidence":[],"type":"unanswerable","difficulty":"easy","answerable":false,"requires_sql":false}
{"id":"minigeo_003","question":"查询某地区识别错误最多的矿物类别需要使用什么类型的数据？","answer":"需要结构化样本预测数据，包括真实类别、预测类别、采样地区和错误计数。","evidence":[],"type":"sql","difficulty":"medium","answerable":true,"requires_sql":true}
```

- [ ] **Step 2: Implement benchmark loader**

Create `scripts/evaluate_bench.py`:

```python
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    path = Path("data/benchmark/minigeo_bench.jsonl")
    rows = load_jsonl(path)
    types = {}
    for row in rows:
        types[row["type"]] = types.get(row["type"], 0) + 1
    print(f"items={len(rows)}")
    print(f"types={types}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run benchmark loader**

Run:

```powershell
python scripts/evaluate_bench.py
```

Expected:

```text
items=3
types={'mineral_property': 1, 'unanswerable': 1, 'sql': 1}
```

### Task 3: Implement RAG Corpus Loader

**Files:**
- Create: `src/minigeo/rag/corpus.py`
- Create: `tests/test_corpus.py`

- [ ] **Step 1: Write corpus loader test**

Create `tests/test_corpus.py`:

```python
from pathlib import Path
from minigeo.rag.corpus import load_corpus


def test_load_corpus_reads_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "corpus.jsonl"
    path.write_text(
        '{"chunk_id":"doc_1#chunk_1","text":"石英是一种常见矿物。","source":"demo"}\n',
        encoding="utf-8",
    )
    rows = load_corpus(path)
    assert len(rows) == 1
    assert rows[0]["chunk_id"] == "doc_1#chunk_1"
    assert "石英" in rows[0]["text"]
```

- [ ] **Step 2: Implement corpus loader**

Create `src/minigeo/rag/corpus.py`:

```python
import json
from pathlib import Path


def load_corpus(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                row = json.loads(line)
                if "chunk_id" not in row or "text" not in row:
                    raise ValueError("Each corpus row must contain chunk_id and text.")
                rows.append(row)
    return rows
```

- [ ] **Step 3: Run test**

Run:

```powershell
$env:PYTHONPATH="src"
pytest tests/test_corpus.py -v
```

Expected: `1 passed`.

### Task 4: Implement Baseline BM25 Retriever

**Files:**
- Create: `src/minigeo/rag/bm25.py`
- Create: `tests/test_bm25.py`

- [ ] **Step 1: Write retriever test**

Create `tests/test_bm25.py`:

```python
from minigeo.rag.bm25 import BM25Retriever


def test_bm25_returns_relevant_chunk() -> None:
    docs = [
        {"chunk_id": "a", "text": "石英 具有 较高 硬度"},
        {"chunk_id": "b", "text": "方解石 遇 稀盐酸 起泡"},
    ]
    retriever = BM25Retriever(docs)
    results = retriever.search("石英 硬度", top_k=1)
    assert results[0]["chunk_id"] == "a"
```

- [ ] **Step 2: Implement BM25 retriever**

Create `src/minigeo/rag/bm25.py`:

```python
from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    return text.lower().split()


class BM25Retriever:
    def __init__(self, docs: list[dict]):
        self.docs = docs
        self.tokens = [tokenize(doc["text"]) for doc in docs]
        self.index = BM25Okapi(self.tokens)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        scores = self.index.get_scores(tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
        results = []
        for idx, score in ranked[:top_k]:
            row = dict(self.docs[idx])
            row["score"] = float(score)
            results.append(row)
        return results
```

- [ ] **Step 3: Run test**

Run:

```powershell
$env:PYTHONPATH="src"
pytest tests/test_bm25.py -v
```

Expected: `1 passed`.

### Task 5: Implement Verifier Data Contract

**Files:**
- Create: `src/minigeo/verifier/types.py`
- Create: `tests/test_verifier_types.py`

- [ ] **Step 1: Write verifier type test**

Create `tests/test_verifier_types.py`:

```python
from minigeo.verifier.types import ClaimVerification


def test_claim_verification_to_dict() -> None:
    item = ClaimVerification(
        claim="石英硬度高。",
        status="supported",
        evidence=["doc_1#chunk_1"],
        confidence=0.9,
    )
    data = item.to_dict()
    assert data["status"] == "supported"
    assert data["evidence"] == ["doc_1#chunk_1"]
```

- [ ] **Step 2: Implement verifier type**

Create `src/minigeo/verifier/types.py`:

```python
from dataclasses import dataclass


@dataclass
class ClaimVerification:
    claim: str
    status: str
    evidence: list[str]
    confidence: float

    def to_dict(self) -> dict:
        return {
            "claim": self.claim,
            "status": self.status,
            "evidence": self.evidence,
            "confidence": self.confidence,
        }
```

- [ ] **Step 3: Run test**

Run:

```powershell
$env:PYTHONPATH="src"
pytest tests/test_verifier_types.py -v
```

Expected: `1 passed`.

