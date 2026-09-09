from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from typing import Protocol

from book_loop.domain.embedding import CanonicalFactEmbedding
from book_loop.domain.models import CanonicalFact
from book_loop.domain.protocols import EmbeddingProvider


class CanonicalFactEmbeddingStore(Protocol):
    def list_canonical_fact_embeddings(
        self, *, fact_ids: list[str]
    ) -> dict[str, CanonicalFactEmbedding]: ...


class EmbeddingCanonicalRetriever:
    """Retrieve Canon facts by cosine similarity using persisted fact vectors."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        *,
        embedding_store: CanonicalFactEmbeddingStore | None = None,
        embedding_model: str | None = None,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> None:
        if top_k < 0:
            raise ValueError("top_k must be non-negative")
        if min_score < -1.0 or min_score > 1.0:
            raise ValueError("min_score must be between -1 and 1")
        if embedding_store is not None and not (embedding_model or "").strip():
            raise ValueError("embedding_model is required when embedding_store is configured")
        self.embedding_provider = embedding_provider
        self.embedding_store = embedding_store
        self.embedding_model = embedding_model
        self.top_k = top_k
        self.min_score = min_score

    def retrieve(self, facts: Iterable[CanonicalFact], *, query: str) -> list[CanonicalFact]:
        if self.top_k == 0 or not query.strip():
            return []

        candidates = list(facts)
        if not candidates:
            return []

        query_vector = tuple(self.embedding_provider.embed(text=query))
        self._validate_vector(query_vector, label="query")
        query_norm = self._norm(query_vector)
        if query_norm == 0.0:
            return []

        persisted = self._load_persisted_embeddings(candidates)
        ranked: list[tuple[float, CanonicalFact]] = []
        for fact in candidates:
            vector = persisted.get(fact.id)
            if vector is None:
                if self.embedding_store is not None:
                    continue
                text = " ".join((fact.statement, fact.subject, fact.predicate, fact.object))
                vector = tuple(self.embedding_provider.embed(text=text))

            self._validate_vector(vector, label=f"fact {fact.id}")
            try:
                score = self._cosine(query_vector, query_norm, vector)
            except ValueError as exc:
                if str(exc) == "embedding dimensions must match":
                    continue
                raise
            if score >= self.min_score:
                ranked.append((score, fact))

        ranked.sort(key=lambda item: (-item[0], item[1].id, item[1].version))
        return [fact for _, fact in ranked[: self.top_k]]

    def _load_persisted_embeddings(
        self, facts: list[CanonicalFact]
    ) -> dict[str, tuple[float, ...]]:
        if self.embedding_store is None:
            return {}
        stored = self.embedding_store.list_canonical_fact_embeddings(
            fact_ids=[fact.id for fact in facts]
        )
        return {
            fact_id: tuple(entry.embedding)
            for fact_id, entry in stored.items()
            if entry.model == self.embedding_model
        }

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
