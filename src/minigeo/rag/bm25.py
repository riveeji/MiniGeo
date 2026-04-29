import math
from collections import Counter
from typing import Any

from minigeo.rag.query_expansion import expand_query_tokens
from minigeo.rag.tokenizer import tokenize


class BM25Retriever:
    def __init__(self, docs: list[dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        if not docs:
            raise ValueError("BM25Retriever requires at least one document.")
        self.docs = docs
        self.k1 = k1
        self.b = b
        self.tokens = [tokenize(str(doc["text"])) for doc in docs]
        self.doc_freq: Counter[str] = Counter()
        for doc_tokens in self.tokens:
            self.doc_freq.update(set(doc_tokens))
        self.avgdl = sum(len(doc_tokens) for doc_tokens in self.tokens) / len(self.tokens)

    def _idf(self, term: str) -> float:
        n_docs = len(self.docs)
        df = self.doc_freq.get(term, 0)
        return math.log(1 + (n_docs - df + 0.5) / (df + 0.5))

    def _score(self, query_tokens: list[str], doc_tokens: list[str]) -> float:
        if not query_tokens or not doc_tokens:
            return 0.0
        counts = Counter(doc_tokens)
        score = 0.0
        doc_len = len(doc_tokens)
        for term in query_tokens:
            freq = counts.get(term, 0)
            if freq == 0:
                continue
            denom = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            score += self._idf(term) * (freq * (self.k1 + 1)) / denom
        return score

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_tokens = tokenize(query) + expand_query_tokens(query)
        scored = [
            (idx, self._score(query_tokens, doc_tokens))
            for idx, doc_tokens in enumerate(self.tokens)
        ]
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]
        results: list[dict[str, Any]] = []
        for idx, score in ranked:
            row = dict(self.docs[idx])
            row["score"] = float(score)
            results.append(row)
        return results
