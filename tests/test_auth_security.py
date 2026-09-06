from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

TEST_SECRET = "test-secret-key-for-auth-security"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://book_loop:book_loop@localhost:5432/book_loop_test",
)
VALID_PASSWORD = "SecurePassword123!"


@pytest.fixture
def client() -> TestClient:
    settings = Settings(database_url=DATABASE_URL, auth_secret_key=TEST_SECRET)
    return TestClient(create_app(Container(settings=settings)))


def register(client: TestClient, email: str) -> dict:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": VALID_PASSWORD, "name": email},
    )
    assert response.status_code == 201
    return response.json()["user"]


def create_book(client: TestClient) -> str:
    response = client.post(
        "/api/books",
        json={
            "title": "Private Book",
            "theme": "Fantasy",
            "author_idea": "A private story",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_book_owner_cannot_be_changed_through_update(client: TestClient) -> None:
    owner = register(client, "owner@example.com")
    client.post("/api/auth/logout")
    attacker = register(client, "attacker@example.com")

    client.post("/api/auth/logout")
    login = client.post(
        "/api/auth/login",
        json={"email": "owner@example.com", "password": VALID_PASSWORD},
    )
    assert login.status_code == 200

    book_id = create_book(client)
    response = client.put(
        f"/api/books/{book_id}",
        json={"owner_id": attacker["id"]},
    )
    assert response.status_code == 400

    stored = client.get(f"/api/books/{book_id}")
    assert stored.status_code == 200
    assert stored.json()["owner_id"] == owner["id"]


def test_invalid_bearer_token_is_rejected(client: TestClient) -> None:
    response = client.get(
        "/api/books/anything",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert response.status_code == 401
