from __future__ import annotations

from typing import Protocol

from book_loop.domain.embedding import CanonicalFactEmbedding
from book_loop.domain.models import CanonicalFact
from book_loop.domain.protocols import EmbeddingProvider


class CanonicalFactEmbeddingStore(Protocol):
    def get_canonical_fact_embedding(
        self, *, fact_id: str
    ) -> CanonicalFactEmbedding | None: ...

    def save_canonical_fact_embedding(self, embedding: CanonicalFactEmbedding) -> None: ...


class CanonicalFactEmbeddingIndexer:
    """Build and persist semantic vectors for canonical facts."""

    def __init__(
        self,
        *,
        provider: EmbeddingProvider,
        repository: CanonicalFactEmbeddingStore,
        model: str,
    ) -> None:
        if not model.strip():
            raise ValueError("An embedding model is required")
        self.provider = provider
        self.repository = repository
        self.model = model

    def index(self, fact: CanonicalFact) -> CanonicalFactEmbedding:
        existing = self.repository.get_canonical_fact_embedding(fact_id=fact.id)
        if existing is not None and existing.model == self.model:
            return existing

        embedding = CanonicalFactEmbedding(
            fact_id=fact.id,
            embedding=tuple(self.provider.embed(text=self._embedding_text(fact))),
            model=self.model,
        )
        self.repository.save_canonical_fact_embedding(embedding)
        return embedding

    @staticmethod
    def _embedding_text(fact: CanonicalFact) -> str:
        text = fact.statement.strip()
        if not text:
            raise ValueError("Canonical fact statement must not be empty")
        return text
