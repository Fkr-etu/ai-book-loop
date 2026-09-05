from __future__ import annotations

import os

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container


def test_health_endpoint() -> None:
    database_url = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")
    settings = Settings(database_url=database_url, auth_secret_key="test-secret-key-for-health")
    client = TestClient(create_app(Container(settings=settings)))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
