from __future__ import annotations

import os

import psycopg
import pytest


@pytest.fixture(autouse=True)
def isolate_postgres_database() -> None:
    """Reset the shared PostgreSQL test database before every test.

    Tests intentionally share one PostgreSQL instance, so deterministic IDs and
    emails must not leak from one test to another. CASCADE also handles foreign
    keys if they are introduced by future migrations.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url or not database_url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
        return

    normalized_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(normalized_url, autocommit=True) as connection:
        tables = connection.execute(
            """
            SELECT tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname = 'public'
              AND tablename <> 'spatial_ref_sys'
            ORDER BY tablename
            """
        ).fetchall()
        if tables:
            quoted_tables = ", ".join(f'"{row[0].replace(chr(34), chr(34) * 2)}"' for row in tables)
            connection.execute(f"TRUNCATE TABLE {quoted_tables} RESTART IDENTITY CASCADE")
