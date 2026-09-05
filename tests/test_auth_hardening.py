from __future__ import annotations

import os

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.auth import COOKIE_NAME
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")


def test_authenticated_user_owns_created_book():
    settings = Settings(database_url=DATABASE_URL, auth_secret_key="test-secret")
    client = TestClient(create_app(Container(settings=settings)))
    register = client.post(
        "/api/auth/register",
        json={"email": "owner@example.com", "password": "password123"},
    )
    assert register.status_code == 201
    assert COOKIE_NAME in register.cookies
    created = client.post(
        "/api/books",
        json={"title": "Private", "theme": "Fantasy", "author_idea": "Idea"},
    )
    assert created.status_code == 200
    assert created.json()["owner_id"]
