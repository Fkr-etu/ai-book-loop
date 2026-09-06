from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.auth import validate_password
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")
VALID_PASSWORD = "SecurePassword123!"


@pytest.mark.parametrize(
    "password",
    [
        "Short1!",
        "alllowercase123!",
        "ALLUPPERCASE123!",
        "NoDigitsHere!",
        "NoSpecial12345",
    ],
)
def test_validate_password_rejects_missing_requirements(password: str) -> None:
    with pytest.raises(ValueError):
        validate_password(password)


def test_validate_password_accepts_strong_password() -> None:
    assert validate_password(VALID_PASSWORD) == VALID_PASSWORD


def test_register_rejects_weak_password() -> None:
    settings = Settings(database_url=DATABASE_URL, auth_secret_key="test-secret-key-for-password-policy")
    client = TestClient(create_app(Container(settings=settings)))
    response = client.post(
        "/api/auth/register",
        json={"email": "weak-password@example.com", "password": "password123"},
    )
    assert response.status_code == 422


def test_register_accepts_strong_password() -> None:
    settings = Settings(database_url=DATABASE_URL, auth_secret_key="test-secret-key-for-password-policy")
    client = TestClient(create_app(Container(settings=settings)))
    response = client.post(
        "/api/auth/register",
        json={"email": "strong-password@example.com", "password": VALID_PASSWORD},
    )
    assert response.status_code == 201
