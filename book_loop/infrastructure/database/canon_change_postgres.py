from book_loop.infrastructure.database.canon_change_repository import CanonChangeRepositoryMixin
from book_loop.infrastructure.database.postgres import PostgresBookRepository


class PostgresCanonChangeRepository(CanonChangeRepositoryMixin, PostgresBookRepository):
    """PostgreSQL repository with Canon change proposal persistence behavior."""

    def __init__(self, database_url: str) -> None:
        super().__init__(database_url)
        self._connection._connection.execute("""
            CREATE TABLE IF NOT EXISTS canon_change_proposals (
                id TEXT PRIMARY KEY,
                book_id TEXT NOT NULL,
                canonical_fact_id TEXT NOT NULL,
                statement TEXT NOT NULL,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                proposer_id TEXT,
                rationale TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'proposed',
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS ix_canon_change_proposals_book
                ON canon_change_proposals(book_id, created_at, id);
            CREATE TABLE IF NOT EXISTS canon_change_review_decisions (
                id TEXT PRIMARY KEY,
                proposal_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                reviewer_id TEXT,
                rationale TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS ix_canon_change_review_decisions_proposal
                ON canon_change_review_decisions(proposal_id, created_at, id);
        """)
        self._connection.commit()
