from __future__ import annotations

import hashlib
from uuid import uuid4

from book_loop.domain.models import Assertion, DocumentChunk, Evidence, IngestionResult, SourceDocument
from book_loop.domain.protocols import AssertionExtractor, KnowledgeRepository


class IngestDocument:
    def __init__(self, *, repository: KnowledgeRepository, extractor: AssertionExtractor, chunk_size: int = 1800) -> None:
        if chunk_size < 1:
            raise ValueError("chunk_size must be positive")
        self._repository = repository
        self._extractor = extractor
        self._chunk_size = chunk_size

    def execute(self, *, book_id: str, name: str, source_type: str, content: str, metadata: dict[str, str] | None = None) -> IngestionResult:
        normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
        if not normalized:
            raise ValueError("Document content must not be empty")
        content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        existing = self._repository.find_source_by_hash(book_id=book_id, content_hash=content_hash)
        if existing is not None:
            return IngestionResult(source_document=existing, already_ingested=True)

        source = SourceDocument(
            id=str(uuid4()), book_id=book_id, name=name.strip(), source_type=source_type.strip(),
            content=normalized, content_hash=content_hash, metadata=metadata or {}, version=1,
        )
        self._repository.save_source(source)
        chunks = self._chunk(source)
        assertions: list[Assertion] = []
        evidence: list[Evidence] = []
        for chunk in chunks:
            self._repository.save_chunk(chunk)
            for extracted in self._extractor.extract(chunk=chunk):
                if extracted.end_offset > len(chunk.content):
                    raise ValueError("Extractor evidence end_offset exceeds chunk length")
                if extracted.start_offset >= extracted.end_offset:
                    raise ValueError("Extractor evidence offsets are invalid")
                evidence_id = str(uuid4())
                assertion_id = str(uuid4())
                excerpt = chunk.content[extracted.start_offset:extracted.end_offset]
                assertion = Assertion(
                    id=assertion_id, source_document_id=source.id, chunk_id=chunk.id,
                    statement=extracted.statement.strip(), subject=extracted.subject.strip(),
                    predicate=extracted.predicate.strip(), object=extracted.object.strip(),
                    confidence=extracted.confidence, evidence_id=evidence_id,
                )
                item = Evidence(
                    id=evidence_id, assertion_id=assertion_id, source_document_id=source.id,
                    chunk_id=chunk.id, start_offset=chunk.start_offset + extracted.start_offset,
                    end_offset=chunk.start_offset + extracted.end_offset, excerpt=excerpt,
                )
                self._repository.save_assertion(assertion)
                self._repository.save_evidence(item)
                assertions.append(assertion)
                evidence.append(item)
        return IngestionResult(source_document=source, chunks=chunks, assertions=assertions, evidence=evidence)

    def _chunk(self, source: SourceDocument) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        start = 0
        sequence = 0
        text = source.content
        while start < len(text):
            end = min(start + self._chunk_size, len(text))
            if end < len(text):
                boundary = max(text.rfind("\n", start, end), text.rfind(" ", start, end))
                if boundary > start + self._chunk_size // 2:
                    end = boundary
            content = text[start:end].strip()
            if content:
                leading = len(text[start:end]) - len(text[start:end].lstrip())
                actual_start = start + leading
                actual_end = actual_start + len(content)
                chunks.append(DocumentChunk(
                    id=str(uuid4()), source_document_id=source.id, content=content,
                    sequence=sequence, start_offset=actual_start, end_offset=actual_end,
                ))
                sequence += 1
            start = end
            while start < len(text) and text[start].isspace():
                start += 1
        return chunks
