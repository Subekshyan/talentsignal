"""Similarity backends: TF-IDF baseline and Sentence-BERT.

Thresholds are PLACEHOLDERS. They must be tuned on your labelled evaluation
set (Phase 1) before you trust any result.
"""
from __future__ import annotations

from typing import Protocol


class Backend(Protocol):
    name: str
    matched_at: float
    partial_at: float

    def fit(self, units: list[str], queries: list[str]) -> None: ...
    def similarities(self, query: str) -> list[float]: ...


class TfidfBackend:
    name = "tfidf"
    matched_at = 0.35
    partial_at = 0.15

    def fit(self, units: list[str], queries: list[str]) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        self._vec.fit(units + queries)
        self._unit_matrix = self._vec.transform(units) if units else None

    def similarities(self, query: str) -> list[float]:
        if self._unit_matrix is None:
            return []
        from sklearn.metrics.pairwise import linear_kernel

        q = self._vec.transform([query])
        return linear_kernel(q, self._unit_matrix).ravel().tolist()


class SbertBackend:
    name = "sbert"
    matched_at = 0.55
    partial_at = 0.40

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "sentence-transformers is not installed. "
                    "Run: pip install sentence-transformers"
                ) from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def fit(self, units: list[str], queries: list[str]) -> None:
        model = self._load()
        self._unit_emb = model.encode(units, normalize_embeddings=True) if units else None

    def similarities(self, query: str) -> list[float]:
        if self._unit_emb is None:
            return []
        q = self._load().encode([query], normalize_embeddings=True)
        return (self._unit_emb @ q[0]).tolist()


def get_backend(name: str) -> Backend:
    if name == "tfidf":
        return TfidfBackend()
    if name == "sbert":
        return SbertBackend()
    raise ValueError(f"unknown backend: {name}")
