from book_loop.infrastructure.database.canon_change_repository import CanonChangeRepositoryMixin
from book_loop.infrastructure.database.postgres import PostgresBookRepository


class PostgresCanonChangeRepository(CanonChangeRepositoryMixin, PostgresBookRepository):
    """PostgreSQL repository with Canon change proposal persistence behavior."""

    pass
