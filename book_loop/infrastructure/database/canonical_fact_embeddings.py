from __future__ import annotations

from typing import Any

from book_loop.domain.embedding import CanonicalFactEmbedding


class CanonicalFactEmbeddingRepositoryMixin:
    """Persistence operations for the semantic index of canonical facts."""

    def save_canonical_fact_embedding(self, embedding: CanonicalFactEmbedding) -> None:
        self._connection.execute(
            """
            INSERT INTO canonical_fact_embeddings(fact_id, embedding, model)
            VALUES(?, ?, ?)
            ON CONFLICT(fact_id) DO UPDATE SET
                embedding = excluded.embedding,
                model = excluded.model
            """,
            (embedding.fact_id, list(embedding.embedding), embedding.model),
        )
        self._connection.commit()

    def get_canonical_fact_embedding(
        self, *, fact_id: str
    ) -> CanonicalFactEmbedding | None:
        row = self._connection.execute(
            "SELECT fact_id, embedding, model FROM canonical_fact_embeddings WHERE fact_id = ?",
            (fact_id,),
        ).fetchone()
        if row is None:
            return None
        return self._canonical_fact_embedding_from_row(row)

    def list_canonical_fact_embeddings(
        self, *, fact_ids: list[str]
    ) -> dict[str, CanonicalFactEmbedding]:
        if not fact_ids:
            return {}
        rows = self._connection.execute(
            "SELECT fact_id, embedding, model FROM canonical_fact_embeddings WHERE fact_id = ANY(?)",
            (fact_ids,),
        ).fetchall()
        return {
            embedding.fact_id: embedding
            for embedding in (self._canonical_fact_embedding_from_row(row) for row in rows)
        }

    @staticmethod
    def _canonical_fact_embedding_from_row(row: Any) -> CanonicalFactEmbedding:
        return CanonicalFactEmbedding(
            fact_id=row["fact_id"],
            embedding=tuple(float(value) for value in row["embedding"]),
            model=row["model"],
        )
