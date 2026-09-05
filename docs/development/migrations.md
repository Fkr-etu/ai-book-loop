# PostgreSQL migrations

The project uses **PostgreSQL as its only supported persistence backend**. Database schema evolution is managed with [Alembic](https://alembic.sqlalchemy.org/).

## Configuration

Alembic reads `DATABASE_URL` from the environment. The URL must use one of:

- `postgresql://...`
- `postgres://...`
- `postgresql+psycopg://...`

Example:

```bash
export DATABASE_URL=postgresql://book_loop:book_loop@localhost:5432/book_loop
```

## Commands

Apply all migrations:

```bash
alembic upgrade head
```

Show the current database revision:

```bash
alembic current
```

Show migration history:

```bash
alembic history
```

Roll back one revision:

```bash
alembic downgrade -1
```

Create a new revision after a schema change:

```bash
alembic revision -m "describe the schema change"
```

## Existing databases

The initial revision is intentionally idempotent (`CREATE TABLE IF NOT EXISTS`) so it can establish Alembic tracking against a database whose schema was already created by the pre-Alembic application.

For an existing database that already has the expected schema, use:

```bash
alembic stamp head
```

Do **not** use `stamp` on an empty database: run `alembic upgrade head` instead.

## Deployment rule

Migrations must run **before application startup** for deployments that introduce schema changes. The application should not rely on runtime table creation as the deployment mechanism.

CI runs `alembic upgrade head` against PostgreSQL 16 before the test suite. This makes migration validity part of the normal verification path.

## Rules for future migrations

1. Never edit an already-applied migration.
2. Add a new revision for every schema change.
3. Keep migrations PostgreSQL-native.
4. Preserve Canon invariants in database constraints/indexes.
5. Test both `upgrade` and, when practical, `downgrade` paths.
6. Keep application code and migrations synchronized in the same pull request.
