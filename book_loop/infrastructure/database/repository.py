from __future__ import annotations

import json
import sqlite3

from book_loop.domain.models import BookState


class SQLiteBookRepository:
    def __init__(self, database_url: str) -> None:
        self._path = database_url.removeprefix("sqlite:///")
        self._connection = sqlite3.connect(self._path)
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS books (id TEXT PRIMARY KEY, data TEXT NOT NULL)"
        )
        self._connection.commit()

    def save(self, book: BookState) -> None:
        data = json.dumps(book.model_dump(mode="json"))
        self._connection.execute(
            "INSERT INTO books(id, data) VALUES(?, ?) "
            "ON CONFLICT(id) DO UPDATE SET data=excluded.data",
            (book.id, data),
        )
        self._connection.commit()

    def get(self, book_id: str) -> BookState:
        row = self._connection.execute(
            "SELECT data FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown book: {book_id}")
        return BookState.model_validate(json.loads(row[0]))
