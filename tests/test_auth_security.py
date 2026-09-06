from __future__ import annotations

import os
import uuid

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


def test_login_is_rate_limited_per_account_and_returns_generic_error(client: TestClient) -> None:
    email = f"ratelimit-{uuid.uuid4().hex}@example.com"
    settings = Settings(
        database_url=DATABASE_URL,
        auth_secret_key=TEST_SECRET,
        auth_login_rate_limit=2,
        auth_login_rate_window_seconds=900,
        auth_login_ip_rate_limit=100,
        auth_login_ip_rate_window_seconds=900,
        auth_register_rate_limit=100,
        auth_register_rate_window_seconds=900,
    )
    limited_client = TestClient(create_app(Container(settings=settings)))
    register(limited_client, email)
    limited_client.post("/api/auth/logout")

    first = limited_client.post("/api/auth/login", json={"email": email, "password": "WrongPassword123!"})
    second = limited_client.post("/api/auth/login", json={"email": email, "password": "WrongPassword123!"})
    blocked = limited_client.post("/api/auth/login", json={"email": email, "password": "WrongPassword123!"})

    assert first.status_code == 401
    assert first.json()["detail"] == "Adresse e-mail ou mot de passe incorrect."
    assert second.status_code == 401
    assert blocked.status_code == 429
    assert blocked.json()["detail"] == "Trop de tentatives. Réessayez dans quelques instants."
    assert blocked.headers["retry-after"] == "60"


def test_login_success_resets_account_failure_counter(client: TestClient) -> None:
    email = f"reset-{uuid.uuid4().hex}@example.com"
    settings = Settings(
        database_url=DATABASE_URL,
        auth_secret_key=TEST_SECRET,
        auth_login_rate_limit=2,
        auth_login_rate_window_seconds=900,
        auth_login_ip_rate_limit=100,
        auth_login_ip_rate_window_seconds=900,
        auth_register_rate_limit=100,
        auth_register_rate_window_seconds=900,
    )
    limited_client = TestClient(create_app(Container(settings=settings)))
    register(limited_client, email)
    limited_client.post("/api/auth/logout")

    assert limited_client.post("/api/auth/login", json={"email": email, "password": "WrongPassword123!"}).status_code == 401
    assert limited_client.post("/api/auth/login", json={"email": email, "password": VALID_PASSWORD}).status_code == 200
    limited_client.post("/api/auth/logout")
    assert limited_client.post("/api/auth/login", json={"email": email, "password": "WrongPassword123!"}).status_code == 401
    assert limited_client.post("/api/auth/login", json={"email": email, "password": "WrongPassword123!"}).status_code == 401
    assert limited_client.post("/api/auth/login", json={"email": email, "password": "WrongPassword123!"}).status_code == 429


def test_register_duplicate_email_does_not_confirm_account_existence(client: TestClient) -> None:
    email = f"duplicate-{uuid.uuid4().hex}@example.com"
    register(client, email)
    client.post("/api/auth/logout")
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": VALID_PASSWORD, "name": "Another author"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Impossible de créer le compte. Vérifiez les informations saisies et réessayez."
