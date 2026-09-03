from __future__ import annotations

from book_loop.application.use_cases.approve_chapter_and_sync_canon import ApproveChapterAndSyncCanon
from book_loop.domain.models import BookState, Chapter, ChapterStatus, ExtractedAssertion


class FakeBookRepository:
    def __init__(self) -> None:
        self.book = BookState(
            id="book-1",
            title="Test",
            theme="Mystery",
            author_idea="Test",
            chapters=[Chapter(
                id="chapter-1",
                number=1,
                title="Discovery",
                objective="Introduce Alice",
                status=ChapterStatus.DRAFT,
                current_version=1,
            )],
        )
        self.draft = "Alice is an archivist. Alice is a detective."

    def get(self, book_id: str) -> BookState:
        assert book_id == self.book.id
        return self.book

    def save(self, book: BookState) -> None:
        self.book = book

    def get_chapter_version(self, book_id: str, chapter_number: int, version: int) -> str:
        assert (book_id, chapter_number, version) == ("book-1", 1, 1)
        return self.draft


class FakeKnowledgeRepository:
    def __init__(self) -> None:
        self.sources = []
        self.chunks = []
        self.assertions = []
        self.evidence = []
        self.conflicts = []

    def find_source_by_hash(self, *, book_id: str, content_hash: str):
        return None

    def save_source(self, source):
        self.sources.append(source)

    def save_chunk(self, chunk):
        self.chunks.append(chunk)

    def save_assertion(self, assertion):
        self.assertions.append(assertion)

    def save_evidence(self, evidence):
        self.evidence.append(evidence)

    def list_assertions(self, *, book_id: str):
        return [assertion for assertion in self.assertions if assertion.book_id == book_id]

    def save_conflict(self, conflict):
        self.conflicts.append(conflict)

    def list_conflicts(self, *, book_id: str):
        return [conflict for conflict in self.conflicts if conflict.book_id == book_id]

    def resolve_conflict(self, left_assertion_id, right_assertion_id, resolution_assertion_id): ...
    def save_review_decision(self, decision): ...
    def next_canonical_version(self, *, book_id: str, subject: str, predicate: str): return 1
    def deactivate_canonical_facts(self, *, book_id: str, subject: str, predicate: str): ...
    def save_canonical_fact(self, fact): ...
    def list_active_canonical_facts(self, *, book_id: str): return []
    def set_assertion_status(self, assertion_id, status): ...


class FakeExtractor:
    def extract(self, *, chunk):
        return [
            ExtractedAssertion(
                statement="Alice is an archivist.",
                subject="Alice",
                predicate="occupation",
                object="archivist",
                confidence=0.99,
                start_offset=0,
                end_offset=len("Alice is an archivist."),
            ),
            ExtractedAssertion(
                statement="Alice is a detective.",
                subject="Alice",
                predicate="occupation",
                object="detective",
                confidence=0.98,
                start_offset=len("Alice is an archivist. "),
                end_offset=len("Alice is an archivist. Alice is a detective."),
            ),
        ]


def test_approval_syncs_approved_version_as_proposed_canon_and_detects_conflict():
    books = FakeBookRepository()
    knowledge = FakeKnowledgeRepository()

    result = ApproveChapterAndSyncCanon(
        book_repository=books,
        knowledge_repository=knowledge,
        extractor=FakeExtractor(),
    ).execute(book=books.book, chapter_number=1)

    assert result.book.chapters[0].status is ChapterStatus.APPROVED
    assert len(result.ingestion.assertions) == 2
    assert all(assertion.status.value == "proposed" for assertion in result.ingestion.assertions)
    assert len(result.ingestion.evidence) == 2
    assert len(result.conflicts) == 1
    assert result.conflicts[0].status.value == "open"
    assert knowledge.conflicts[0].left_assertion_id != knowledge.conflicts[0].right_assertion_id
