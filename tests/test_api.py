from __future__ import annotations

import tempfile
import pytest
from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container


@pytest.fixture
def test_client():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_url = f"sqlite:///{tmp.name}"
        settings = Settings(database_url=db_url)
        container = Container(settings=settings)
        app = create_app(container)
        yield TestClient(app)


def test_get_book(test_client):
    response = test_client.get("/api/books/proj-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "proj-001"
    assert "title" in data
    assert "chapters" in data


def test_create_book(test_client):
    payload = {
        "title": "Nouveau Livre",
        "theme": "Quête de sagesse",
        "author_idea": "Un voyageur de l'éther",
        "lore": "Magie des étoiles",
        "constraints": ["Pas d'anachronismes"]
    }
    response = test_client.post("/api/books", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Nouveau Livre"
    assert data["author_idea"] == "Un voyageur de l'éther"


def test_outline_workflow(test_client):
    # 1. Generate outline
    res = test_client.post("/api/books/proj-001/outline/generate")
    assert res.status_code == 200
    book = res.json()
    assert book["outline"] is not None

    # 2. Approve outline
    res = test_client.post("/api/books/proj-001/outline/approve")
    assert res.status_code == 200
    book = res.json()
    assert book["outline_approved"] is True

    # 3. Add chapter
    res = test_client.post("/api/books/proj-001/chapters", json={"title": "Chapitre 3", "objective": "Découverte"})
    assert res.status_code == 200
    book = res.json()
    assert len(book["chapters"]) == 3


def test_generate_and_review_chapter(test_client):
    # Ensure outline approved
    test_client.post("/api/books/proj-001/outline/approve")

    # Generate Chapter 1
    res = test_client.post("/api/books/proj-001/chapters/1/generate")
    assert res.status_code == 200
    gen_data = res.json()
    assert gen_data["versionNumber"] >= 1

    # Get Canonical Context
    res = test_client.get("/api/books/proj-001/chapters/1/context")
    assert res.status_code == 200
    ctx = res.json()
    assert "formattedContext" in ctx
    assert "AUTHOR IDEA:" in ctx["formattedContext"]

    # Review Chapter
    res = test_client.post("/api/books/proj-001/chapters/1/review", json={"draftText": "Un texte scholastique et poétique."})
    assert res.status_code == 200
    rev_data = res.json()
    assert rev_data["review"]["approved"] is True


def test_api_error_handling_and_not_found(test_client):
    # 404 for non-existent book
    res = test_client.get("/api/books/unknown-id")
    assert res.status_code == 404

    # Create a new book with unapproved outline
    res_create = test_client.post("/api/books", json={
        "title": "Book Test",
        "theme": "Theme",
        "author_idea": "Idea"
    })
    book_id = res_create.json()["id"]

    # 400 when attempting to add chapter before outline approved
    res = test_client.post(f"/api/books/{book_id}/chapters", json={"title": "Chap", "objective": "Obj"})
    assert res.status_code == 400


def test_approve_and_reject_chapter_api(test_client):
    test_client.post("/api/books/proj-001/outline/approve")
    test_client.post("/api/books/proj-001/chapters/1/generate")

    # Approve chapter 1
    res_app = test_client.post("/api/books/proj-001/chapters/1/approve")
    assert res_app.status_code == 200
    assert res_app.json()["chapters"][0]["status"] == "approved"

    # Reject chapter 2
    res_rej = test_client.post("/api/books/proj-001/chapters/2/reject")
    assert res_rej.status_code == 200
    assert res_rej.json()["chapters"][1]["status"] == "rejected"
