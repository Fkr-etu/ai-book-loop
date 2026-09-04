from __future__ import annotations

from book_loop.domain.models import DocumentChunk, Evidence, SourceDocument
from book_loop.infrastructure.database.repository import SQLiteBookRepository


def test_list_evidence_returns_only_evidence_for_requested_book(tmp_path):
    repository = SQLiteBookRepository(str(tmp_path / "knowledge.db"))

    source_a = SourceDocument(
        id="source-a", book_id="book-a", name="chapter-1", source_type="text",
        content="Alice lives in Marseille.", content_hash="a" * 64,
    )
    source_b = SourceDocument(
        id="source-b", book_id="book-b", name="chapter-1", source_type="text",
        content="Bob lives in Paris.", content_hash="b" * 64,
    )
    repository.save_source(source_a)
    repository.save_source(source_b)

    repository.save_chunk(DocumentChunk(
        id="chunk-a", source_document_id=source_a.id, content=source_a.content,
        sequence=0, start_offset=0, end_offset=len(source_a.content),
    ))
    repository.save_chunk(DocumentChunk(
        id="chunk-b", source_document_id=source_b.id, content=source_b.content,
        sequence=0, start_offset=0, end_offset=len(source_b.content),
    ))

    repository.save_evidence(Evidence(
        id="evidence-a", assertion_id="assertion-a", source_document_id=source_a.id,
        chunk_id="chunk-a", start_offset=0, end_offset=25, excerpt=source_a.content,
    ))
    repository.save_evidence(Evidence(
        id="evidence-b", assertion_id="assertion-b", source_document_id=source_b.id,
        chunk_id="chunk-b", start_offset=0, end_offset=20, excerpt=source_b.content,
    ))

    evidence = repository.list_evidence(book_id="book-a")

    assert [item.id for item in evidence] == ["evidence-a"]
    assert evidence[0].assertion_id == "assertion-a"
    assert evidence[0].excerpt == source_a.content
