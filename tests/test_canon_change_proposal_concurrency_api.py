from __future__ import annotations

import hashlib
import os

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.domain.models import Assertion, AssertionStatus, CanonicalFact, DocumentChunk, Evidence, SourceDocument
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

TEST_SECRET = "test-secret-key-for-canon-concurrency-api"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")
VALID_PASSWORD = "SecurePassword123!"


def setup_client():
    settings = Settings(database_url=DATABASE_URL, auth_secret_key=TEST_SECRET)
    container = Container(settings=settings)
    client = TestClient(create_app(container))
    response = client.post(
        "/api/auth/register",
        json={"email": "canon-concurrency@example.com", "password": VALID_PASSWORD, "name": "Canon Concurrency"},
    )
    assert response.status_code == 201
    book = client.post(
        "/api/books",
        json={"title": "Canon Concurrency API", "theme": "Mystery", "author_idea": "Test", "lore": "Lore"},
    )
    assert book.status_code == 200
    return client, container, book.json()["id"]


def test_second_proposal_on_same_fact_is_rejected_after_first_acceptance():
    client, container, book_id = setup_client()
    source_id = "source-concurrency"
    chunk_id = "chunk-concurrency"
    evidence_id = "evidence-concurrency"
    content = "Alice lives in Paris."
    container.repository.save_source(
        SourceDocument(
            id=source_id,
            book_id=book_id,
            name="Concurrency test source",
            source_type="test",
            content=content,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
        )
    )
    container.repository.save_chunk(
        DocumentChunk(
            id=chunk_id,
            source_document_id=source_id,
            content=content,
            sequence=0,
            start_offset=0,
            end_offset=len(content),
        )
    )
    assertion = Assertion(
        id="assertion-concurrency",
        source_document_id=source_id,
        chunk_id=chunk_id,
        statement=content,
        subject="Alice",
        predicate="lives_in",
        object="Paris",
        confidence=1.0,
        status=AssertionStatus.ACCEPTED,
        evidence_id=evidence_id,
    )
    container.repository.save_assertion(assertion)
    container.repository.save_evidence(
        Evidence(
            id=evidence_id,
            assertion_id=assertion.id,
            source_document_id=source_id,
            chunk_id=chunk_id,
            start_offset=0,
            end_offset=len(content),
            excerpt=content,
        )
    )
    container.repository.save_canonical_fact(
        CanonicalFact(
            id="fact-concurrency",
            book_id=book_id,
            assertion_id=assertion.id,
            statement=assertion.statement,
            subject=assertion.subject,
            predicate=assertion.predicate,
            object=assertion.object,
            decision_id="decision-concurrency",
            version=1,
            active=True,
            previous_fact_id=None,
        )
    )

    first = client.post(
        f"/api/books/{book_id}/canon-change-proposals",
        json={"fact_id": "fact-concurrency", "statement": "Alice lives in Lyon.", "object": "Lyon", "rationale": "First edit"},
    )
    second = client.post(
        f"/api/books/{book_id}/canon-change-proposals",
        json={"fact_id": "fact-concurrency", "statement": "Alice lives in Marseille.", "object": "Marseille", "rationale": "Second edit"},
    )
    assert first.status_code == 201
    assert second.status_code == 201

    accepted = client.post(
        f"/api/books/{book_id}/canon-change-proposals/{first.json()['id']}/review",
        json={"decision": "accept", "rationale": "Use the first proposal"},
    )
    assert accepted.status_code == 200

    stale = client.post(
        f"/api/books/{book_id}/canon-change-proposals/{second.json()['id']}/review",
        json={"decision": "accept", "rationale": "Try stale proposal"},
    )
    assert stale.status_code == 409
    assert "stale" in stale.json()["detail"].lower()

    facts = client.get(f"/api/books/{book_id}/canonical-facts")
    assert facts.status_code == 200
    active_facts = facts.json()["facts"]
    assert len(active_facts) == 1
    assert active_facts[0]["object"] == "Lyon"
    assert active_facts[0]["version"] == 2

    proposals = client.get(f"/api/books/{book_id}/canon-change-proposals")
    assert proposals.status_code == 200
    statuses = {proposal["id"]: proposal["status"] for proposal in proposals.json()["proposals"]}
    assert statuses[first.json()["id"]] == "accepted"
    assert statuses[second.json()["id"]] == "proposed"
