from __future__ import annotations

import os
import uuid

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.domain.models import BookState, User
from book_loop.infrastructure.auth import hash_password
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container


TEST_SECRET = "test-secret-key-for-books"
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")
VALID_PASSWORD = "SecurePassword123!"


def _user(email: str) -> User:
    return User(
        id=f"usr-{uuid.uuid4().hex}",
        email=email,
        password_hash=hash_password(VALID_PASSWORD),
        name=email.split("@")[0],
    )


def _book(owner_id: str, title: str) -> BookState:
    return BookState(
        id=f"book-{uuid.uuid4().hex}",
        owner_id=owner_id,
        title=title,
        theme="Cohérence narrative",
        author_idea="Une histoire de test.",
    )


def _client() -> tuple[Container, TestClient]:
    settings = Settings(database_url=DATABASE_URL, auth_secret_key=TEST_SECRET, auth_cookie_secure=False)
    container = Container(settings=settings)
    return container, TestClient(create_app(container))


def test_list_books_requires_authentication() -> None:
    _, client = _client()
    assert client.get("/api/books").status_code == 401


def test_list_books_returns_only_current_users_books() -> None:
    container, client = _client()
    user_a = _user(f"author-a-{uuid.uuid4().hex}@example.com")
    user_b = _user(f"author-b-{uuid.uuid4().hex}@example.com")
    container.repository.create_user(user_a)
    container.repository.create_user(user_b)
    book_a = _book(user_a.id, "Livre de A")
    book_b = _book(user_b.id, "Livre de B")
    container.repository.save(book_a)
    container.repository.save(book_b)

    login = client.post("/api/auth/login", json={"email": user_a.email, "password": VALID_PASSWORD})
    assert login.status_code == 200

    response = client.get("/api/books")
    assert response.status_code == 200
    assert [book["id"] for book in response.json()] == [book_a.id]
    assert response.json()[0]["title"] == "Livre de A"


def test_list_books_returns_empty_collection_for_new_user() -> None:
    container, client = _client()
    user = _user(f"empty-{uuid.uuid4().hex}@example.com")
    container.repository.create_user(user)

    login = client.post("/api/auth/login", json={"email": user.email, "password": VALID_PASSWORD})
    assert login.status_code == 200

    response = client.get("/api/books")
    assert response.status_code == 200
    assert response.json() == []
