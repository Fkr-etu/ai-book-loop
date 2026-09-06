from __future__ import annotations

import os

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")
VALID_PASSWORD = "SecurePassword123!"


def test_free_plan_exposes_plan_and_enforces_project_capacity():
    settings = Settings(database_url=DATABASE_URL, auth_secret_key="test-secret-key-for-billing")
    client = TestClient(create_app(Container(settings=settings)))
    email = "capacity-test@example.com"

    register = client.post("/api/auth/register", json={"email": email, "password": VALID_PASSWORD, "name": "Capacity"})
    assert register.status_code == 201
    assert register.json()["user"]["plan"] == "free"
    assert client.get("/api/auth/me").json()["user"]["plan"] == "free"

    payload = {"title": "First", "theme": "Fantasy", "author_idea": "Idea"}
    assert client.post("/api/books", json=payload).status_code == 200
    second = client.post("/api/books", json={**payload, "title": "Second"})
    assert second.status_code == 429


def test_invalid_bearer_token_cannot_create_a_book():
    settings = Settings(database_url=DATABASE_URL, auth_secret_key="test-secret-key-for-billing")
    client = TestClient(create_app(Container(settings=settings)))
    response = client.post(
        "/api/books",
        headers={"Authorization": "Bearer definitely-invalid"},
        json={"title": "Blocked", "theme": "Fantasy", "author_idea": "Idea"},
    )
    assert response.status_code == 401
