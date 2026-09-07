from __future__ import annotations

import hashlib
import os

from fastapi.testclient import TestClient

from book_loop.api.app import create_app
from book_loop.domain.models import Assertion, AssertionStatus, CanonicalFact, DocumentChunk, Evidence, SourceDocument
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

TEST_SECRET = "test-secret-key-for-canon-api"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")
VALID_PASSWORD = "SecurePassword123!"


def setup_client():
    settings = Settings(database_url=DATABASE_URL, auth_secret_key=TEST_SECRET)
    container = Container(settings=settings)
    client = TestClient(create_app(container))
    response = client.post(
        "/api/auth/register",
        json={"email": "impact@example.com", "password": VALID_PASSWORD, "name": "Impact Reviewer"},
    )
    assert response.status_code == 201
    book = client.post(
        "/api/books",
        json={"title": "Canon Impact API", "theme": "Mystery", "author_idea": "Test", "lore": "Lore"},
    )
    assert book.status_code == 200
    return client, container, book.json()["id"]


def test_analyze_canon_change_api_returns_evidence_backed_findings():
    client, container, book_id = setup_client()
    source = SourceDocument(
        id="source-impact", book_id=book_id, name="Impact source", source_type="test",
        content="Alice is parent of Bob.", content_hash=hashlib.sha256(b"Alice is parent of Bob.").hexdigest(),
    )
    chunk = DocumentChunk(
        id="chunk-impact", source_document_id=source.id, content=source.content,
        sequence=0, start_offset=0, end_offset=len(source.content),
    )
    first_assertion = Assertion(
        id="assertion-impact-1", source_document_id=source.id, chunk_id=chunk.id,
        statement="Alice parent_of Bob", subject="Alice", predicate="parent_of", object="Bob",
        confidence=0.95, status=AssertionStatus.ACCEPTED, evidence_id="evidence-impact-1",
    )
    second_assertion = Assertion(
        id="assertion-impact-2", source_document_id=source.id, chunk_id=chunk.id,
        statement="Bob parent_of Claire", subject="Bob", predicate="parent_of", object="Claire",
        confidence=0.95, status=AssertionStatus.ACCEPTED, evidence_id="evidence-impact-2",
    )
    container.repository.save_source(source)
    container.repository.save_chunk(chunk)
    container.repository.save_assertion(first_assertion)
    container.repository.save_assertion(second_assertion)
    container.repository.save_evidence(Evidence(
        id="evidence-impact-1", assertion_id=first_assertion.id, source_document_id=source.id,
        chunk_id=chunk.id, start_offset=0, end_offset=len(source.content), excerpt=source.content,
    ))
    container.repository.save_evidence(Evidence(
        id="evidence-impact-2", assertion_id=second_assertion.id, source_document_id=source.id,
        chunk_id=chunk.id, start_offset=0, end_offset=len(source.content), excerpt=source.content,
    ))
    container.repository.save_canonical_fact(CanonicalFact(
        id="fact-impact-1", book_id=book_id, assertion_id=first_assertion.id,
        statement=first_assertion.statement, subject="Alice", predicate="parent_of", object="Bob",
        decision_id="decision-impact-1", version=1, active=True, previous_fact_id=None,
    ))
    container.repository.save_canonical_fact(CanonicalFact(
        id="fact-impact-2", book_id=book_id, assertion_id=second_assertion.id,
        statement=second_assertion.statement, subject="Bob", predicate="parent_of", object="Claire",
        decision_id="decision-impact-2", version=1, active=True, previous_fact_id=None,
    ))

    response = client.get(f"/api/books/{book_id}/canonical-facts/fact-impact-1/impact")

    assert response.status_code == 200
    assert response.json() == {
        "changed_fact_id": "fact-impact-1",
        "findings": [{
            "fact_id": "fact-impact-2",
            "assertion_id": "assertion-impact-2",
            "statement": "Bob parent_of Claire",
            "source_document_id": source.id,
            "chunk_id": chunk.id,
            "excerpt": source.content,
            "start_offset": 0,
            "end_offset": len(source.content),
            "risk": "high",
            "dependency_depth": 1,
        }],
    }
