from __future__ import annotations

import hashlib
from collections.abc import Callable
from uuid import NAMESPACE_URL, uuid5

from book_loop.domain.models import Assertion, DocumentChunk, Evidence, IngestionResult, SourceDocument
from book_loop.domain.protocols import AssertionExtractor, KnowledgeRepository
from book_loop.domain.temporal import AssertionTemporalContextStore, TemporalScope, TemporalScopeKind


class IngestDocument:
    def __init__(
        self,
        *,
        repository: KnowledgeRepository,
        extractor: AssertionExtractor,
        chunk_size: int = 1800,
        temporal_context_store: AssertionTemporalContextStore | None = None,
    ) -> None:
        if chunk_size < 1:
            raise ValueError("chunk_size must be positive")
        self._repository = repository
        self._extractor = extractor
        self._chunk_size = chunk_size
        self._temporal_context_store = temporal_context_store

    def execute(
        self,
        *,
        book_id: str,
        name: str,
        source_type: str,
        content: str,
        metadata: dict[str, str] | None = None,
    ) -> IngestionResult:
        source, chunks, already_ingested = self.prepare(
            book_id=book_id,
            name=name,
            source_type=source_type,
            content=content,
            metadata=metadata,
        )
        if already_ingested:
            return IngestionResult(source_document=source, already_ingested=True)
        assertions, evidence = self.process_source(source=source, chunks=chunks)
        return IngestionResult(source_document=source, chunks=chunks, assertions=assertions, evidence=evidence)

    def prepare(
        self,
        *,
        book_id: str,
        name: str,
        source_type: str,
        content: str,
        metadata: dict[str, str] | None = None,
    ) -> tuple[SourceDocument, list[DocumentChunk], bool]:
        normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
        if not normalized:
            raise ValueError("Document content must not be empty")
        content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        existing = self._repository.find_source_by_hash(book_id=book_id, content_hash=content_hash)
        if existing is not None:
            return existing, [], True

        source_metadata = metadata or {}
        source = SourceDocument(
            id=str(uuid5(NAMESPACE_URL, f"book-loop:source:{book_id}:{content_hash}")),
            book_id=book_id, name=name.strip(), source_type=source_type.strip(),
            content=normalized, content_hash=content_hash, metadata=source_metadata, version=1,
        )
        self._repository.save_source(source)
        chunks = self._chunk(source)
        for chunk in chunks:
            self._repository.save_chunk(chunk)
        return source, chunks, False

    def process_by_hash(
        self,
        *,
        book_id: str,
        content_hash: str,
        on_chunk_progress: Callable[[int, int], None] | None = None,
    ) -> IngestionResult:
        source = self._repository.find_source_by_hash(book_id=book_id, content_hash=content_hash)
        if source is None:
            raise KeyError(content_hash)
        chunks = self._chunk(source)
        assertions_by_chunk: dict[str, list[Assertion]] = {}
        for assertion in self._repository.list_assertions(book_id=book_id):
            if assertion.source_document_id == source.id:
                assertions_by_chunk.setdefault(assertion.chunk_id, []).append(assertion)
        assertions, evidence = self.process_source(
            source=source,
            chunks=chunks,
            existing_assertions_by_chunk=assertions_by_chunk,
            on_chunk_progress=on_chunk_progress,
        )
        return IngestionResult(source_document=source, chunks=chunks, assertions=assertions, evidence=evidence)

    def process_source(
        self,
        *,
        source: SourceDocument,
        chunks: list[DocumentChunk],
        existing_assertions_by_chunk: dict[str, list[Assertion]] | None = None,
        on_chunk_progress: Callable[[int, int], None] | None = None,
    ) -> tuple[list[Assertion], list[Evidence]]:
        assertions: list[Assertion] = []
        evidence: list[Evidence] = []
        temporal_scope = self._temporal_scope(source.metadata)
        total = len(chunks)
        existing_assertions_by_chunk = existing_assertions_by_chunk or {}
        for index, chunk in enumerate(chunks, start=1):
            existing_assertions = existing_assertions_by_chunk.get(chunk.id, [])
            if existing_assertions:
                assertions.extend(existing_assertions)
            else:
                for extracted in self._extractor.extract(chunk=chunk):
                    if extracted.end_offset > len(chunk.content):
                        raise ValueError("Extractor evidence end_offset exceeds chunk length")
                    if extracted.start_offset >= extracted.end_offset:
                        raise ValueError("Extractor evidence offsets are invalid")
                    evidence_id = str(uuid5(NAMESPACE_URL, f"book-loop:evidence:{chunk.id}:{extracted.start_offset}:{extracted.end_offset}"))
                    assertion_id = str(uuid5(NAMESPACE_URL, f"book-loop:assertion:{chunk.id}:{extracted.start_offset}:{extracted.end_offset}:{extracted.statement.strip()}"))
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
                    if self._temporal_context_store is not None and temporal_scope is not None:
                        self._temporal_context_store.save_temporal_scope(assertion_id=assertion.id, scope=temporal_scope)
                    self._repository.save_evidence(item)
                    assertions.append(assertion)
                    evidence.append(item)
            if on_chunk_progress is not None:
                on_chunk_progress(index, total)
        return assertions, evidence

    @staticmethod
    def _temporal_scope(metadata: dict[str, str]) -> TemporalScope | None:
        chapter_number = metadata.get("chapter_number", "").strip()
        if not chapter_number:
            return None
        try:
            position = int(chapter_number)
        except ValueError as exc:
            raise ValueError("chapter_number metadata must be an integer") from exc
        if position < 0:
            raise ValueError("chapter_number metadata must be non-negative")
        return TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=position)

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
                    id=str(uuid5(NAMESPACE_URL, f"book-loop:chunk:{source.id}:{sequence}:{actual_start}:{actual_end}")),
                    source_document_id=source.id, content=content,
                    sequence=sequence, start_offset=actual_start, end_offset=actual_end,
                ))
                sequence += 1
            start = end
            while start < len(text) and text[start].isspace():
                start += 1
        return chunks
