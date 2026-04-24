import hashlib
import math
from typing import Any, Protocol

from minigeo.rag.tokenizer import tokenize


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]:
        ...


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Vectors must have the same length.")
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    value = dot / (left_norm * right_norm)
    return max(-1.0, min(1.0, value))


class HashingEmbedder:
    def __init__(self, dimensions: int = 256):
        if dimensions <= 0:
            raise ValueError("dimensions must be positive.")
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            index = int(digest[:8], 16) % self.dimensions
            sign = 1.0 if int(digest[8:10], 16) % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class DenseRetriever:
    def __init__(self, docs: list[dict[str, Any]], embedder: Embedder | None = None):
        if not docs:
            raise ValueError("DenseRetriever requires at least one document.")
        self.docs = docs
        self.embedder = embedder or HashingEmbedder()
        self.doc_vectors = [self.embedder.embed(str(doc["text"])) for doc in docs]

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_vector = self.embedder.embed(query)
        scored = [
            (idx, cosine_similarity(query_vector, doc_vector))
            for idx, doc_vector in enumerate(self.doc_vectors)
        ]
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]
        results: list[dict[str, Any]] = []
        for idx, score in ranked:
            row = dict(self.docs[idx])
            row["dense_score"] = float(score)
            results.append(row)
        return results

