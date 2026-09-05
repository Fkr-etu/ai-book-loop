from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

TEST_SECRET = "test-secret-key-for-api"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")


@pytest.fixture
def test_client():
    settings = Settings(database_url=DATABASE_URL, auth_secret_key=TEST_SECRET)
    client = TestClient(create_app(Container(settings=settings)))
    response = client.post("/api/auth/register", json={"email": "author@example.com", "password": "password123", "name": "Author"})
    assert response.status_code == 201
    yield client


def create_book(test_client: TestClient, title: str = "Test Book") -> str:
    response = test_client.post("/api/books", json={"title": title, "theme": "Fantasy", "author_idea": "Une quête initiatique", "lore": "Un monde ancien", "constraints": ["Pas d'anachronismes"]})
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
    edited = {"outline": {"chapters": [{"number": 1, "title": "Chapitre 1", "objective": "Départ"}, {"number": 2, "title": "Chapitre 2", "objective": "Montée des enjeux"}, {"number": 3, "title": "Chapitre 3", "objective": "Résolution"}]}}
    assert test_client.put(f"/api/books/{book_id}/outline", json=edited).status_code == 200
    assert test_client.post(f"/api/books/{book_id}/outline/approve").json()["outline_approved"] is True
    for chapter_number in (1, 2, 3):
        res = test_client.post(f"/api/books/{book_id}/chapters", json={"chapter_number": chapter_number})
        assert res.status_code == 200
    assert res.json()["chapters"][-1]["number"] == 3


def test_generate_chapter_api_runs_complete_loop(test_client):
    book_id = create_book(test_client, "Chapter Loop Test")
    outline = {"outline": {"chapters": [{"number": 1, "title": "Le Fragment", "objective": "Découvrir le premier fragment mémoire"}, {"number": 2, "title": "La Trace", "objective": "Suivre la piste laissée par le fragment"}]}}
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


def test_books_are_isolated_between_users(test_client):
    book_id = create_book(test_client, "Private Book")
    test_client.post("/api/auth/logout")
    assert test_client.post("/api/auth/login", json={"email": "b@example.com", "password": "password123"}).status_code == 401
    register = test_client.post("/api/auth/register", json={"email": "b@example.com", "password": "password123"})
    assert register.status_code == 201
    assert test_client.get(f"/api/books/{book_id}").status_code == 404
    assert test_client.post(f"/api/books/{book_id}/outline/generate").status_code == 404


def test_document_ingestion_and_assertion_review(test_client):
    book_id = create_book(test_client, "Ingestion Test Book")
    res = test_client.post(f"/api/books/{book_id}/documents/ingest", json={"name": "Manuscrit Source", "sourceType": "markdown", "content": "Valerius est né à Aethelgard en l'an 1042. Il possède la relique d'obsidienne."})
    assert res.status_code == 200
    data = res.json()
    assert data["source_document"]["name"] == "Manuscrit Source"
    assert "assertions" in data
    assertions = test_client.get(f"/api/books/{book_id}/assertions").json()["assertions"]
    assert len(assertions) >= 1
    assertion_id = assertions[0]["id"]
    review_res = test_client.post(f"/api/books/{book_id}/assertions/{assertion_id}/review", json={"decision": "accept", "rationale": "Information confirmée"})
    assert review_res.status_code == 200
    assert review_res.json()["decision"] == "accept"


def test_approving_chapter_syncs_proposed_canon(test_client):
    book_id = create_book(test_client, "Canon Approval Test")
    outline = {"outline": {"chapters": [{"number": 1, "title": "Le Fragment", "objective": "Découvrir le fragment"}]}}
    assert test_client.put(f"/api/books/{book_id}/outline", json=outline).status_code == 200
    assert test_client.post(f"/api/books/{book_id}/outline/approve").status_code == 200
    assert test_client.post(f"/api/books/{book_id}/chapters", json={"chapter_number": 1}).status_code == 200
    assert test_client.post(f"/api/books/{book_id}/chapters/1/generate").status_code == 200
    response = test_client.post(f"/api/books/{book_id}/chapters/1/approve")
    assert response.status_code == 200
    data = response.json()
    assert data["chapters"][0]["status"] == "approved"
    assert data["canonSync"]["assertionCount"] == 1
    assert data["canonSync"]["evidenceCount"] == 1
    assert data["canonSync"]["sourceDocument"]["source_type"] == "approved_chapter"
    assertions = test_client.get(f"/api/books/{book_id}/assertions").json()["assertions"]
    assert len(assertions) == 1
    assert assertions[0]["status"] == "proposed"
