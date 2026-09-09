from __future__ import annotations

from book_loop.application.use_cases.ingest_document import IngestDocument
from book_loop.domain.models import DocumentChunk, ExtractedAssertion
from book_loop.domain.temporal import TemporalScopeKind
from book_loop.infrastructure.database.temporal_context import TemporalContextStore


class Cursor:
    def __init__(self, row=None):
        self._row = row

    def fetchone(self):
        return self._row


class Connection:
    def __init__(self) -> None:
        self.rows = {}

    def execute(self, sql, params=()):
        if sql.lstrip().startswith("INSERT INTO assertion_temporal_contexts"):
            assertion_id, kind, position = params
            self.rows[assertion_id] = {"kind": kind, "position": position}
            return Cursor()
        if "SELECT kind, position FROM assertion_temporal_contexts" in sql:
            row = self.rows.get(params[0])
            return Cursor(row)
        raise AssertionError(f"Unexpected SQL: {sql}")

    def commit(self):
        pass


class Repository:
    def __init__(self) -> None:
        self._connection = Connection()
        self.sources = []
        self.chunks = []
        self.assertions = []
        self.evidence = []

    def find_source_by_hash(self, *, book_id: str, content_hash: str):
        return None

    def save_source(self, source): self.sources.append(source)
    def save_chunk(self, chunk): self.chunks.append(chunk)
    def save_assertion(self, assertion): self.assertions.append(assertion)
    def save_evidence(self, evidence): self.evidence.append(evidence)


class Extractor:
    def extract(self, *, chunk: DocumentChunk):
        return [ExtractedAssertion(
            statement="Elara porte Givre-Âme",
            subject="Elara",
            predicate="porte",
            object="Givre-Âme",
            confidence=1.0,
            start_offset=0,
            end_offset=len(chunk.content),
        )]


def test_chapter_ingestion_persists_story_point_for_each_assertion():
    repository = Repository()
    temporal_context_store = TemporalContextStore(repository)
    result = IngestDocument(
        repository=repository,
        extractor=Extractor(),
        temporal_context_store=temporal_context_store,
    ).execute(
        book_id="book-1",
        name="Chapter 3",
        source_type="approved_chapter",
        content="Elara porte Givre-Âme",
        metadata={"chapter_number": "3", "chapter_version": "1"},
    )

    assertion_id = result.assertions[0].id
    scope = temporal_context_store.get_temporal_scope(assertion_id=assertion_id)

    assert scope is not None
    assert scope.kind is TemporalScopeKind.STORY_POINT
    assert scope.position == 3


def test_non_chapter_ingestion_does_not_create_temporal_scope():
    repository = Repository()
    result = IngestDocument(repository=repository, extractor=Extractor()).execute(
        book_id="book-1",
        name="Notes",
        source_type="text",
        content="Elara porte Givre-Âme",
    )

    assert TemporalContextStore(repository).get_temporal_scope(
        assertion_id=result.assertions[0].id
    ) is None
