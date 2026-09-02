from __future__ import annotations

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container
from book_loop.infrastructure.database.repository import SQLiteBookRepository
from book_loop.domain.models import User
from book_loop.infrastructure.auth import (
    COOKIE_NAME,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

TEST_SECRET = "test-secret-key-for-auth"


def test_password_hashing():
    pwd = "MySecretPassword123"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token():
    user = User(id="usr-1", email="test@example.com", password_hash="dummy", name="Test User")
    token = create_access_token(user, secret_key=TEST_SECRET)
    decoded = decode_access_token(token, secret_key=TEST_SECRET)
    assert decoded is not None
    assert decoded["sub"] == "usr-1"
    assert "email" not in decoded


def test_user_repository_crud(tmp_path):
    db_path = f"sqlite:///{tmp_path}/test.db"
    repo = SQLiteBookRepository(db_path)
    user = User(
        id="usr-test-1",
        email="AUTHOR@example.com",
        password_hash=hash_password("password123"),
        name="Auteur Test",
    )
    created = repo.create_user(user)
    assert created.id == "usr-test-1"
    assert created.email == "author@example.com"
    assert repo.get_user_by_email("author@example.com") is not None
    assert repo.get_user_by_id("usr-test-1") is not None


def test_auth_endpoints_flow(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path}/test.db", auth_secret_key=TEST_SECRET)
    client = TestClient(create_app(Container(settings=settings)))

    assert client.get("/api/auth/me").status_code == 401

    payload = {
        "email": "newauthor@manuscript.studio",
        "password": "securePassword123",
        "name": "Nouveau Romancier",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    assert COOKIE_NAME in response.cookies
    assert client.get("/api/auth/me").status_code == 200

    assert client.post("/api/auth/register", json=payload).status_code == 400
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/auth/login", json={"email": payload["email"], "password": "wrong"}).status_code == 401
    assert client.post("/api/auth/login", json=payload).status_code == 200
