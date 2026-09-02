from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

from book_loop.domain.models import CanonicalFact


class EmbeddingProvider:
    """Protocol-like base contract for text embedding providers.

    Concrete providers may call a local model or an external embedding API.
    The retrieval layer remains independent of that implementation.
    """

    def embed(self, *, text: str) -> Sequence[float]:
        raise NotImplementedError


class EmbeddingCanonicalRetriever:
    """Retrieve Canon facts by cosine similarity over text embeddings."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        *,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> None:
        if top_k < 0:
            raise ValueError("top_k must be non-negative")
        if min_score < -1.0 or min_score > 1.0:
            raise ValueError("min_score must be between -1 and 1")
        self.embedding_provider = embedding_provider
        self.top_k = top_k
        self.min_score = min_score

    def retrieve(self, facts: Iterable[CanonicalFact], *, query: str) -> list[CanonicalFact]:
        if self.top_k == 0 or not query.strip():
            return []

        query_vector = tuple(self.embedding_provider.embed(text=query))
        self._validate_vector(query_vector, label="query")
        query_norm = self._norm(query_vector)
        if query_norm == 0.0:
            return []

        ranked: list[tuple[float, CanonicalFact]] = []
        for fact in facts:
            text = " ".join((fact.statement, fact.subject, fact.predicate, fact.object))
            vector = tuple(self.embedding_provider.embed(text=text))
            self._validate_vector(vector, label=f"fact {fact.id}")
            score = self._cosine(query_vector, query_norm, vector)
            if score >= self.min_score:
                ranked.append((score, fact))

        ranked.sort(key=lambda item: (-item[0], item[1].id, item[1].version))
        return [fact for _, fact in ranked[: self.top_k]]

    @staticmethod
    def _validate_vector(vector: Sequence[float], *, label: str) -> None:
        if not vector:
            raise ValueError(f"{label} embedding must not be empty")
        if not all(math.isfinite(value) for value in vector):
            raise ValueError(f"{label} embedding must contain finite values")

    @staticmethod
    def _norm(vector: Sequence[float]) -> float:
        return math.sqrt(sum(value * value for value in vector))

    @classmethod
    def _cosine(
        cls,
        left: Sequence[float],
        left_norm: float,
        right: Sequence[float],
    ) -> float:
        if len(left) != len(right):
            raise ValueError("embedding dimensions must match")
        right_norm = cls._norm(right)
        if right_norm == 0.0:
            return 0.0
        return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)
