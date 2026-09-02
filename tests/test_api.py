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
    assert data["outline"]["chapters"][0]["number"] == 1


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
    res = test_client.post("/api/books/proj-001/outline/generate")
    assert res.status_code == 200
    book = res.json()
    assert book["outline"] is not None
    assert book["outline"]["chapters"]

    edited = {
        "outline": {
            "chapters": [
                {"number": 1, "title": "Chapitre 1", "objective": "Départ"},
                {"number": 2, "title": "Chapitre 2", "objective": "Montée des enjeux"},
                {"number": 3, "title": "Chapitre 3", "objective": "Résolution"},
            ]
        }
    }
    res = test_client.put("/api/books/proj-001/outline", json=edited)
    assert res.status_code == 200
    assert res.json()["outline_approved"] is False

    res = test_client.post("/api/books/proj-001/outline/approve")
    assert res.status_code == 200
    assert res.json()["outline_approved"] is True

    res = test_client.post("/api/books/proj-001/chapters", json={"chapter_number": 3})
    assert res.status_code == 200
    book = res.json()
    assert book["chapters"][-1]["number"] == 3
    assert book["chapters"][-1]["title"] == "Chapitre 3"


def test_generate_and_review_chapter(test_client):
    test_client.post("/api/books/proj-001/outline/approve")

    res = test_client.post("/api/books/proj-001/chapters/1/generate")
    assert res.status_code == 200
    gen_data = res.json()
    assert gen_data["versionNumber"] >= 1

    res = test_client.get("/api/books/proj-001/chapters/1/context")
    assert res.status_code == 200
    ctx = res.json()
    assert "formattedContext" in ctx
    assert "AUTHOR IDEA:" in ctx["formattedContext"]
    assert ctx["globalOutline"]["chapters"][0]["number"] == 1

    res = test_client.post("/api/books/proj-001/chapters/1/review", json={"draftText": "Un texte scholastique et poétique."})
    assert res.status_code == 200
    rev_data = res.json()
    assert rev_data["review"]["approved"] is True


def test_api_error_handling_and_not_found(test_client):
    res = test_client.get("/api/books/unknown-id")
    assert res.status_code == 404

    res_create = test_client.post("/api/books", json={
        "title": "Book Test",
        "theme": "Theme",
        "author_idea": "Idea"
    })
    book_id = res_create.json()["id"]

    res = test_client.post(f"/api/books/{book_id}/chapters", json={"chapter_number": 1})
    assert res.status_code == 400


def test_approve_and_reject_chapter_api(test_client):
    test_client.post("/api/books/proj-001/outline/approve")
    test_client.post("/api/books/proj-001/chapters/1/generate")

    res_app = test_client.post("/api/books/proj-001/chapters/1/approve")
    assert res_app.status_code == 200
    assert res_app.json()["chapters"][0]["status"] == "approved"

    res_rej = test_client.post("/api/books/proj-001/chapters/2/reject")
    assert res_rej.status_code == 200
    assert res_rej.json()["chapters"][1]["status"] == "rejected"
