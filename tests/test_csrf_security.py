from __future__ import annotations

import os

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://book_loop:book_loop@localhost:5432/book_loop_test",
)
VALID_PASSWORD = "ValidPassword1!"


def _client() -> TestClient:
    settings = Settings(
        database_url=DATABASE_URL,
        auth_secret_key="test-secret-key-for-csrf",
        auth_cookie_secure=True,
        cors_allowed_origins=["http://localhost:3000"],
    )
    return TestClient(create_app(Container(settings=settings)), base_url="https://localhost")


def _register(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "email": "csrf@example.com",
            "password": VALID_PASSWORD,
            "name": "CSRF Test",
        },
    )
    assert response.status_code == 201


def test_cookie_authenticated_mutation_requires_allowed_origin() -> None:
    client = _client()
    _register(client)

    response = client.post(
        "/api/books",
        json={"title": "Livre", "theme": "Test", "author_idea": "Idée"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Requête d'origine non autorisée."


def test_cookie_authenticated_mutation_rejects_foreign_origin() -> None:
    client = _client()
    _register(client)

    response = client.post(
        "/api/books",
        headers={"Origin": "https://attacker.example"},
        json={"title": "Livre", "theme": "Test", "author_idea": "Idée"},
    )

    assert response.status_code == 403


def test_cookie_authenticated_mutation_accepts_configured_origin() -> None:
    client = _client()
    _register(client)

    response = client.post(
        "/api/books",
        headers={"Origin": "http://localhost:3000"},
        json={"title": "Livre", "theme": "Test", "author_idea": "Idée"},
    )

    assert response.status_code == 200
