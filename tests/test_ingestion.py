from __future__ import annotations

import hashlib

import pytest

from book_loop.application.use_cases.ingest_document import IngestDocument
from book_loop.domain.models import DocumentChunk, ExtractedAssertion


class FakeRepository:
    def __init__(self) -> None:
        self.sources = []
        self.chunks = []
        self.assertions = []
        self.evidence = []

    def find_source_by_hash(self, *, book_id: str, content_hash: str):
        return next((s for s in self.sources if s.book_id == book_id and s.content_hash == content_hash), None)

    def save_source(self, source): self.sources.append(source)
    def save_chunk(self, chunk): self.chunks.append(chunk)
    def save_assertion(self, assertion): self.assertions.append(assertion)
    def save_evidence(self, evidence): self.evidence.append(evidence)


class FakeExtractor:
    def __init__(self, assertions=None) -> None:
        self.assertions = assertions or []
        self.calls = 0

    def extract(self, *, chunk: DocumentChunk):
        self.calls += 1
        return self.assertions


def test_ingests_document_with_traceable_evidence():
    repository = FakeRepository()
    extractor = FakeExtractor([
        ExtractedAssertion(
            statement="Alice is 32 years old",
            subject="Alice",
            predicate="age",
            object="32",
            confidence=0.95,
            start_offset=0,
            end_offset=19,
        )
    ])

    result = IngestDocument(repository=repository, extractor=extractor, chunk_size=100).execute(
        book_id="book-1", name="notes.txt", source_type="text", content="Alice is 32 years old."
    )

    assert result.already_ingested is False
    assert len(result.chunks) == 1
    assert len(result.assertions) == 1
    assert result.assertions[0].status.value == "proposed"
    assert result.assertions[0].evidence_id == result.evidence[0].id
    assert result.evidence[0].excerpt == "Alice is 32 years old"
    assert len(repository.sources) == len(repository.chunks) == len(repository.assertions) == len(repository.evidence) == 1


def test_ingestion_is_idempotent_by_content_hash():
    repository = FakeRepository()
    extractor = FakeExtractor()
    use_case = IngestDocument(repository=repository, extractor=extractor)
    content = "The castle stands on the hill."

    first = use_case.execute(book_id="book-1", name="a.txt", source_type="text", content=content)
    second = use_case.execute(book_id="book-1", name="a.txt", source_type="text", content=content)

    expected_hash = hashlib.sha256(content.encode()).hexdigest()
    assert first.source_document.content_hash == expected_hash
    assert second.already_ingested is True
    assert second.source_document.id == first.source_document.id
    assert extractor.calls == 1


def test_empty_document_is_rejected():
    with pytest.raises(ValueError, match="must not be empty"):
        IngestDocument(repository=FakeRepository(), extractor=FakeExtractor()).execute(
            book_id="book-1", name="empty.txt", source_type="text", content="  \n  "
        )


def test_invalid_extractor_offsets_are_rejected():
    extractor = FakeExtractor([
        ExtractedAssertion(
            statement="bad", subject="x", predicate="y", object="z", confidence=0.5,
            start_offset=0, end_offset=999,
        )
    ])
    with pytest.raises(ValueError, match="exceeds chunk length"):
        IngestDocument(repository=FakeRepository(), extractor=extractor).execute(
            book_id="book-1", name="a.txt", source_type="text", content="short"
        )
