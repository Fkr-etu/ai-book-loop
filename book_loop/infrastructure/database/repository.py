from __future__ import annotations

import json
import sqlite3

from book_loop.domain.models import BookState, SceneReview, User


class SQLiteBookRepository:
    def __init__(self, database_url: str) -> None:
        self._path = database_url.removeprefix("sqlite:///")
        self._connection = sqlite3.connect(self._path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (id TEXT PRIMARY KEY, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS chapter_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id TEXT NOT NULL,
                chapter_number INTEGER NOT NULL,
                version INTEGER NOT NULL,
                draft TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(book_id, chapter_number, version)
            );
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id TEXT NOT NULL,
                chapter_number INTEGER NOT NULL,
                version INTEGER NOT NULL,
                score INTEGER NOT NULL,
                approved INTEGER NOT NULL,
                issues TEXT NOT NULL,
                suggestions TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
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
        return BookState.model_validate(json.loads(row["data"]))

    def save_chapter_version(self, book_id: str, chapter_number: int, version: int, draft: str) -> None:
        self._connection.execute(
            "INSERT INTO chapter_versions(book_id, chapter_number, version, draft) VALUES(?, ?, ?, ?)",
            (book_id, chapter_number, version, draft),
        )
        self._connection.commit()

    def save_review(self, book_id: str, chapter_number: int, version: int, review: SceneReview) -> None:
        self._connection.execute(
            "INSERT INTO reviews(book_id, chapter_number, version, score, approved, issues, suggestions) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (book_id, chapter_number, version, review.score, int(review.approved),
             json.dumps(review.issues), json.dumps(review.suggestions)),
        )
        self._connection.commit()

    def create_user(self, user: User) -> User:
        self._connection.execute(
            "INSERT INTO users(id, email, password_hash, name) VALUES(?, ?, ?, ?)",
            (user.id, user.email.lower().strip(), user.password_hash, user.name),
        )
        self._connection.commit()
        return self.get_user_by_email(user.email)  # type: ignore

    def get_user_by_email(self, email: str) -> User | None:
        row = self._connection.execute(
            "SELECT id, email, password_hash, name, created_at FROM users WHERE lower(email) = ?",
            (email.lower().strip(),)
        ).fetchone()
        if row is None:
            return None
        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            name=row["name"],
            created_at=row["created_at"],
        )

    def get_user_by_id(self, user_id: str) -> User | None:
        row = self._connection.execute(
            "SELECT id, email, password_hash, name, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        if row is None:
            return None
        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            name=row["name"],
            created_at=row["created_at"],
        )
