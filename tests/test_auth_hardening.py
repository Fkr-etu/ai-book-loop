from __future__ import annotations

import tempfile

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container
from book_loop.infrastructure.auth import COOKIE_NAME


def test_auth_secret_is_required():
    settings = Settings(auth_secret_key="")
    client = TestClient(create_app(Container(settings=settings)))
    response = client.post(
        "/api/auth/register",
        json={"email": "author@example.com", "password": "password123"},
    )
    assert response.status_code == 500


def test_authenticated_user_owns_created_book():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        settings = Settings(database_url=f"sqlite:///{tmp.name}", auth_secret_key="test-secret")
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
