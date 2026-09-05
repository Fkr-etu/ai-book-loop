from __future__ import annotations

import hashlib
import os

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.domain.models import Assertion, AssertionStatus, Conflict, ConflictStatus, DocumentChunk, Evidence, SourceDocument
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

TEST_SECRET = "test-secret-key-for-canon-api"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")


def setup_client():
    settings = Settings(database_url=DATABASE_URL, auth_secret_key=TEST_SECRET)
    container = Container(settings=settings)
    client = TestClient(create_app(container))
    response = client.post("/api/auth/register", json={"email": "canon@example.com", "password": "password123", "name": "Canon Reviewer"})
    assert response.status_code == 201
    book = client.post("/api/books", json={"title": "Canon API", "theme": "Mystery", "author_idea": "Test", "lore": "Lore"})
    assert book.status_code == 200
    return client, container, book.json()["id"]


def seed_assertion(container: Container, book_id: str, *, assertion_id: str = "assertion-1", object_value: str = "Marseille") -> Assertion:
    source_id = f"source-{assertion_id}"
    chunk_id = f"chunk-{assertion_id}"
    evidence_id = f"evidence-{assertion_id}"
    content = f"Céleste vit à {object_value}."
    source = SourceDocument(id=source_id, book_id=book_id, name="Test source", source_type="test", content=content, content_hash=hashlib.sha256(content.encode()).hexdigest())
    chunk = DocumentChunk(id=chunk_id, source_document_id=source_id, content=content, sequence=0, start_offset=0, end_offset=len(content))
    assertion = Assertion(id=assertion_id, source_document_id=source_id, chunk_id=chunk_id, statement=content, subject="Céleste", predicate="lives_in", object=object_value, confidence=0.95, status=AssertionStatus.PROPOSED, evidence_id=evidence_id)
    evidence = Evidence(id=evidence_id, assertion_id=assertion_id, source_document_id=source_id, chunk_id=chunk_id, start_offset=0, end_offset=len(content), excerpt=content)
    container.repository.save_source(source)
    container.repository.save_chunk(chunk)
    container.repository.save_assertion(assertion)
    container.repository.save_evidence(evidence)
    return assertion


def test_canon_review_endpoints_expose_conflicts_and_facts():
    client, container, book_id = setup_client()
    first = seed_assertion(container, book_id, assertion_id="assertion-1", object_value="Marseille")
    second = seed_assertion(container, book_id, assertion_id="assertion-2", object_value="Aubagne")
    container.repository.save_conflict(Conflict(id="conflict-1", book_id=book_id, left_assertion_id=first.id, right_assertion_id=second.id, status=ConflictStatus.OPEN))
    conflicts = client.get(f"/api/books/{book_id}/conflicts")
    assert conflicts.status_code == 200
    assert conflicts.json()["conflicts"][0]["status"] == "open"
    facts = client.get(f"/api/books/{book_id}/canonical-facts")
    assert facts.status_code == 200
    assert facts.json()["facts"] == []


def test_accept_review_promotes_assertion_to_canonical_fact():
    client, container, book_id = setup_client()
    assertion = seed_assertion(container, book_id)
    response = client.post(f"/api/books/{book_id}/assertions/{assertion.id}/review", json={"decision": "accept", "rationale": "Validated by author"})
    assert response.status_code == 200
    assert response.json()["decision"] == "accept"
    assertions = client.get(f"/api/books/{book_id}/assertions").json()["assertions"]
    assert assertions[0]["status"] == "accepted"
    facts = client.get(f"/api/books/{book_id}/canonical-facts").json()["facts"]
    assert len(facts) == 1
    assert facts[0]["assertion_id"] == assertion.id
    assert facts[0]["active"] is True
    assert facts[0]["decision_id"] == response.json()["id"]


def test_reject_and_defer_do_not_create_canonical_facts():
    client, container, book_id = setup_client()
    rejected = seed_assertion(container, book_id, assertion_id="reject-me", object_value="Marseille")
    deferred = seed_assertion(container, book_id, assertion_id="defer-me", object_value="Aubagne")
    assert client.post(f"/api/books/{book_id}/assertions/{rejected.id}/review", json={"decision": "reject", "rationale": "Contradicted by source"}).status_code == 200
    assert client.post(f"/api/books/{book_id}/assertions/{deferred.id}/review", json={"decision": "defer", "rationale": "Need more evidence"}).status_code == 200
    assert client.get(f"/api/books/{book_id}/canonical-facts").json()["facts"] == []
    assertions = {item["id"]: item for item in client.get(f"/api/books/{book_id}/assertions").json()["assertions"]}
    assert assertions[rejected.id]["status"] == "rejected"
    assert assertions[deferred.id]["status"] == "deferred"


def test_canon_review_api_respects_book_ownership():
    client_a, container, book_id = setup_client()
    assertion = seed_assertion(container, book_id)
    settings = Settings(database_url=DATABASE_URL, auth_secret_key=TEST_SECRET)
    client_b = TestClient(create_app(Container(settings=settings)))
    assert client_b.post("/api/auth/register", json={"email": "other@example.com", "password": "password123", "name": "Other"}).status_code == 201
    assert client_b.get(f"/api/books/{book_id}/assertions").status_code == 404
    assert client_b.get(f"/api/books/{book_id}/conflicts").status_code == 404
    assert client_b.get(f"/api/books/{book_id}/canonical-facts").status_code == 404
    assert client_b.post(f"/api/books/{book_id}/assertions/{assertion.id}/review", json={"decision": "accept"}).status_code == 404
