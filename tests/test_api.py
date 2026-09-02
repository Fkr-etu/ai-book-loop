from __future__ import annotations

import tempfile

import pytest
from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

TEST_SECRET = "test-secret-key-for-api"


@pytest.fixture
def test_client():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        settings = Settings(database_url=f"sqlite:///{tmp.name}", auth_secret_key=TEST_SECRET)
        client = TestClient(create_app(Container(settings=settings)))
        response = client.post(
            "/api/auth/register",
            json={"email": "author@example.com", "password": "password123", "name": "Author"},
        )
        assert response.status_code == 201
        yield client


def create_book(test_client: TestClient, title: str = "Test Book") -> str:
    response = test_client.post(
        "/api/books",
        json={
            "title": title,
            "theme": "Fantasy",
            "author_idea": "Une quête initiatique",
            "lore": "Un monde ancien",
            "constraints": ["Pas d'anachronismes"],
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_get_book(test_client):
    book_id = create_book(test_client)
    response = test_client.get(f"/api/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert "title" in data
    assert "chapters" in data
    assert data["owner_id"]


def test_create_book(test_client):
    book_id = create_book(test_client, "Nouveau Livre")
    data = test_client.get(f"/api/books/{book_id}").json()
    assert data["title"] == "Nouveau Livre"
    assert data["author_idea"] == "Une quête initiatique"


def test_outline_workflow(test_client):
    book_id = create_book(test_client, "Outline Test")
    res = test_client.post(f"/api/books/{book_id}/outline/generate")
    assert res.status_code == 200
    assert res.json()["outline"]["chapters"]

    edited = {
        "outline": {
            "chapters": [
                {"number": 1, "title": "Chapitre 1", "objective": "Départ"},
                {"number": 2, "title": "Chapitre 2", "objective": "Montée des enjeux"},
                {"number": 3, "title": "Chapitre 3", "objective": "Résolution"},
            ]
        }
    }
    assert test_client.put(f"/api/books/{book_id}/outline", json=edited).status_code == 200
    assert test_client.post(f"/api/books/{book_id}/outline/approve").json()["outline_approved"] is True

    for chapter_number in (1, 2, 3):
        res = test_client.post(f"/api/books/{book_id}/chapters", json={"chapter_number": chapter_number})
        assert res.status_code == 200
    assert res.json()["chapters"][-1]["number"] == 3


def test_generate_chapter_api_runs_complete_loop(test_client):
    book_id = create_book(test_client, "Chapter Loop Test")
    outline = {
        "outline": {
            "chapters": [
                {"number": 1, "title": "Le Fragment", "objective": "Découvrir le premier fragment mémoire"},
                {"number": 2, "title": "La Trace", "objective": "Suivre la piste laissée par le fragment"},
            ]
        }
    }
    assert test_client.put(f"/api/books/{book_id}/outline", json=outline).status_code == 200
    assert test_client.post(f"/api/books/{book_id}/outline/approve").status_code == 200
    assert test_client.post(f"/api/books/{book_id}/chapters", json={"chapter_number": 1}).status_code == 200

    res = test_client.post(f"/api/books/{book_id}/chapters/1/generate")
    assert res.status_code == 200
    data = res.json()
    assert data["versionNumber"] == 1
    assert data["content"]
    assert data["book"]["chapters"][0]["status"] == "approved"
    assert data["book"]["chapters"][0]["current_version"] == 1
    assert data["book"]["chapters"][0]["summary"] == "Résumé canonique du chapitre."

    context = test_client.get(f"/api/books/{book_id}/chapters/1/context").json()
    assert context["currentObjective"] == "Découvrir le premier fragment mémoire"
    assert "AUTHOR IDEA:" in context["formattedContext"]

    assert test_client.post(f"/api/books/{book_id}/chapters/2/generate").status_code == 400
    assert test_client.post(f"/api/books/{book_id}/chapters", json={"chapter_number": 2}).status_code == 200
    assert test_client.post(f"/api/books/{book_id}/chapters/2/generate").status_code == 200
    context = test_client.get(f"/api/books/{book_id}/chapters/2/context").json()
    assert "Résumé canonique du chapitre." in context["previousSummaries"]


def test_api_requires_authentication(test_client):
    test_client.post("/api/auth/logout")
    assert test_client.get("/api/books/anything").status_code == 401
    assert test_client.post("/api/books", json={"title": "x", "theme": "x", "author_idea": "x"}).status_code == 401


def test_books_are_isolated_between_users(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path}/test.db", auth_secret_key=TEST_SECRET)
    client_a = TestClient(create_app(Container(settings=settings)))
    assert client_a.post("/api/auth/register", json={"email": "a@example.com", "password": "password123"}).status_code == 201
    book_id = create_book(client_a, "Private Book")

    client_b = TestClient(create_app(Container(settings=settings)))
    assert client_b.post("/api/auth/register", json={"email": "b@example.com", "password": "password123"}).status_code == 201
    assert client_b.get(f"/api/books/{book_id}").status_code == 404
    assert client_b.post(f"/api/books/{book_id}/outline/generate").status_code == 404
