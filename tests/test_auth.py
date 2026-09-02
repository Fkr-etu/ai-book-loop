from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.database.repository import SQLiteBookRepository
from book_loop.infrastructure.container import Container
from book_loop.domain.models import User
from book_loop.infrastructure.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    COOKIE_NAME,
)


def test_password_hashing():
    pwd = "MySecretPassword123"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token():
    user = User(id="usr-1", email="test@example.com", password_hash="dummy", name="Test User")
    token = create_access_token(user)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "usr-1"
    assert decoded["email"] == "test@example.com"


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

    fetched_by_email = repo.get_user_by_email("author@example.com")
    assert fetched_by_email is not None
    assert fetched_by_email.id == "usr-test-1"

    fetched_by_id = repo.get_user_by_id("usr-test-1")
    assert fetched_by_id is not None
    assert fetched_by_id.email == "author@example.com"


def test_auth_endpoints_flow(tmp_path):
    db_url = f"sqlite:///{tmp_path}/test.db"
    settings = Settings(database_url=db_url)
    container = Container(settings=settings)
    app = create_app(container)
    client = TestClient(app)

    # 1. Unauthenticated /api/auth/me should return 401
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401

    # 2. Register user
    reg_payload = {
        "email": "newauthor@manuscript.studio",
        "password": "securePassword123",
        "name": "Nouveau Romanctier",
    }
    resp = client.post("/api/auth/register", json=reg_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "user" in data
    assert data["user"]["email"] == "newauthor@manuscript.studio"
    assert COOKIE_NAME in resp.cookies

    # 3. Check /api/auth/me with set-cookie session
    resp_me = client.get("/api/auth/me")
    assert resp_me.status_code == 200
    assert resp_me.json()["user"]["email"] == "newauthor@manuscript.studio"

    # 4. Duplicate registration should fail
    resp_dup = client.post("/api/auth/register", json=reg_payload)
    assert resp_dup.status_code == 400

    # 5. Logout
    resp_logout = client.post("/api/auth/logout")
    assert resp_logout.status_code == 200

    # 6. /api/auth/me after logout should return 401
    resp_me_after = client.get("/api/auth/me")
    assert resp_me_after.status_code == 401

    # 7. Login with invalid password
    resp_bad_login = client.post(
        "/api/auth/login",
        json={"email": "newauthor@manuscript.studio", "password": "wrong"},
    )
    assert resp_bad_login.status_code == 401

    # 8. Login with correct credentials
    resp_login = client.post(
        "/api/auth/login",
        json={"email": "newauthor@manuscript.studio", "password": "securePassword123"},
    )
    assert resp_login.status_code == 200
    assert COOKIE_NAME in resp_login.cookies
