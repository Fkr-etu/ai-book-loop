from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

TEST_SECRET = "test-secret-key-for-character-api"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")
PASSWORD = "SecurePassword123!"


def make_client(email: str) -> TestClient:
    settings = Settings(database_url=DATABASE_URL, auth_secret_key=TEST_SECRET)
    client = TestClient(create_app(Container(settings=settings)))
    response = client.post("/api/auth/register", json={"email": email, "password": PASSWORD, "name": "Author"})
    assert response.status_code == 201
    return client


@pytest.fixture
def client():
    return make_client("character@example.com")


def create_book(client: TestClient, title: str = "Character Book") -> str:
    response = client.post("/api/books", json={"title": title, "theme": "Roman", "author_idea": "Une histoire"})
    assert response.status_code == 200
    return response.json()["id"]


def test_character_crud_and_relations(client: TestClient):
    book_id = create_book(client)

    alice = client.post(f"/api/books/{book_id}/characters", json={"name": "Alice", "aliases": ["Al"], "summary": "Protagoniste", "attributes": {"age": "30"}})
    bob = client.post(f"/api/books/{book_id}/characters", json={"name": "Bob"})
    assert alice.status_code == 201
    assert bob.status_code == 201
    alice_id = alice.json()["id"]
    bob_id = bob.json()["id"]
    assert alice.json()["status"] == "proposed"

    listed = client.get(f"/api/books/{book_id}/characters")
    assert listed.status_code == 200
    assert {item["name"] for item in listed.json()} == {"Alice", "Bob"}

    fetched = client.get(f"/api/books/{book_id}/characters/{alice_id}")
    assert fetched.status_code == 200
    assert fetched.json()["attributes"]["age"] == "30"

    updated = client.put(f"/api/books/{book_id}/characters/{alice_id}", json={"summary": "Héroïne", "status": "active"})
    assert updated.status_code == 200
    assert updated.json()["summary"] == "Héroïne"
    assert updated.json()["status"] == "active"

    relation = client.post(f"/api/books/{book_id}/characters/{alice_id}/relations", json={"target_character_id": bob_id, "relation_type": "rivalité"})
    assert relation.status_code == 201
    relation_id = relation.json()["id"]
    assert relation.json()["status"] == "proposed"

    relations = client.get(f"/api/books/{book_id}/characters/relations")
    assert relations.status_code == 200
    assert relations.json()[0]["relation_type"] == "rivalité"

    assert client.delete(f"/api/books/{book_id}/characters/relations/{relation_id}").status_code == 204
    assert client.get(f"/api/books/{book_id}/characters/relations").json() == []
    assert client.delete(f"/api/books/{book_id}/characters/{alice_id}").status_code == 204
    assert client.get(f"/api/books/{book_id}/characters/{alice_id}").status_code == 404


def test_character_api_does_not_cross_book_boundary(client: TestClient):
    book_a = create_book(client, "Book A")
    character = client.post(f"/api/books/{book_a}/characters", json={"name": "Private"})
    assert character.status_code == 201
    character_id = character.json()["id"]

    # The free tier intentionally allows only one active book per account.
    # Use a second authenticated account to obtain another book without
    # weakening the production capacity rule; the API must still reject
    # access to a character belonging to the first book.
    other_client = make_client("character-other@example.com")
    book_b = create_book(other_client, "Book B")

    assert other_client.get(f"/api/books/{book_b}/characters/{character_id}").status_code == 404
    assert other_client.put(f"/api/books/{book_b}/characters/{character_id}", json={"name": "Stolen"}).status_code == 404
    assert other_client.delete(f"/api/books/{book_b}/characters/{character_id}").status_code == 404
