from book_loop.infrastructure.database.postgres import _normalize_postgres_url


def test_normalize_postgres_url_accepts_psycopg_scheme() -> None:
    assert _normalize_postgres_url("postgresql+psycopg://user:pass@host/db") == "postgresql://user:pass@host/db"


def test_normalize_postgres_url_keeps_libpq_urls() -> None:
    url = "postgresql://user:pass@host/db?sslmode=require"
    assert _normalize_postgres_url(url) == url
