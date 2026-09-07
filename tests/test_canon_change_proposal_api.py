from __future__ import annotations

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.domain.models import CanonicalFact
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

TEST_SECRET = "test-secret-key-for-canon-proposal-api"
DATABASE_URL = "postgresql://book_loop:book_loop@localhost:5432/book_loop_test"
VALID_PASSWORD = "SecurePassword123!"


def setup_client():
    settings = Settings(database_url=DATABASE_URL, auth_secret_key=TEST_SECRET)
    container = Container(settings=settings)
    client = TestClient(create_app(container))
    response = client.post("/api/auth/register", json={"email": "proposal@example.com", "password": VALID_PASSWORD, "name": "Proposal Author"})
    assert response.status_code == 201
    book = client.post("/api/books", json={"title": "Proposal API", "theme": "Mystery", "author_idea": "Test", "lore": "Lore"})
    assert book.status_code == 200
    return client, container, book.json()["id"]


def make_fact(book_id: str, fact_id: str = "fact-proposal-1") -> CanonicalFact:
    return CanonicalFact(id=fact_id, book_id=book_id, assertion_id=f"assertion-{fact_id}", statement="Alice lives in Paris.", subject="Alice", predicate="lives_in", object="Paris", decision_id=f"decision-{fact_id}")


def test_create_and_list_canon_change_proposal_without_mutating_active_fact():
    client, container, book_id = setup_client()
    fact = make_fact(book_id)
    container.repository.save_canonical_fact(fact)
    response = client.post(f"/api/books/{book_id}/canon-change-proposals", json={"fact_id": fact.id, "statement": "Alice lives in Lyon.", "object": "Lyon", "rationale": "Story revision"})
    assert response.status_code == 201
    proposal = response.json()
    assert proposal["status"] == "proposed"
    assert proposal["canonical_fact_id"] == fact.id
    assert proposal["subject"] == "Alice"
    assert proposal["predicate"] == "lives_in"
    assert proposal["object"] == "Lyon"
    assert proposal["proposer_id"]
    listed = client.get(f"/api/books/{book_id}/canon-change-proposals")
    assert listed.status_code == 200
    assert listed.json()["proposals"] == [proposal]
    active = client.get(f"/api/books/{book_id}/canonical-facts").json()["facts"]
    assert active == [fact.model_dump(mode="json")]


def test_proposal_api_rejects_unknown_fact_and_empty_fields():
    client, container, book_id = setup_client()
    fact = make_fact(book_id, "fact-validation")
    container.repository.save_canonical_fact(fact)
    unknown = client.post(f"/api/books/{book_id}/canon-change-proposals", json={"fact_id": "missing", "statement": "Alice lives in Lyon.", "object": "Lyon"})
    assert unknown.status_code == 404
    empty_statement = client.post(f"/api/books/{book_id}/canon-change-proposals", json={"fact_id": fact.id, "statement": "", "object": "Lyon"})
    assert empty_statement.status_code == 400
    empty_object = client.post(f"/api/books/{book_id}/canon-change-proposals", json={"fact_id": fact.id, "statement": "Alice lives in Lyon.", "object": ""})
    assert empty_object.status_code == 400


def test_proposal_api_respects_book_ownership():
    client, container, book_id = setup_client()
    fact = make_fact(book_id, "fact-owner")
    container.repository.save_canonical_fact(fact)
    other = TestClient(create_app(Container(settings=Settings(database_url=DATABASE_URL, auth_secret_key=TEST_SECRET))))
    assert other.post("/api/auth/register", json={"email": "proposal-other@example.com", "password": VALID_PASSWORD, "name": "Other"}).status_code == 201
    assert other.get(f"/api/books/{book_id}/canon-change-proposals").status_code == 404
    assert other.post(f"/api/books/{book_id}/canon-change-proposals", json={"fact_id": fact.id, "statement": "Changed", "object": "Lyon"}).status_code == 404
