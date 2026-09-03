from __future__ import annotations

from book_loop.application.use_cases.extract_chapter_assertions import ExtractChapterAssertions
from book_loop.domain.models import BookState, Chapter, ChapterStatus, ExtractedAssertion


class FakeBookRepository:
    def __init__(self, book: BookState, draft: str = "Alice is an archivist.") -> None:
        self.book = book
        self.draft = draft

    def get(self, book_id: str) -> BookState:
        assert book_id == self.book.id
        return self.book

    def get_chapter_version(self, book_id: str, chapter_number: int, version: int) -> str:
        assert (book_id, chapter_number, version) == (self.book.id, 1, 1)
        return self.draft


class FakeKnowledgeRepository:
    def __init__(self) -> None:
        self.sources = []
        self.chunks = []
        self.assertions = []
        self.evidence = []

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
        return self.assertions

    def save_conflict(self, conflict): ...
    def resolve_conflict(self, left_assertion_id, right_assertion_id, resolution_assertion_id): ...
    def save_review_decision(self, decision): ...
    def next_canonical_version(self, *, book_id: str, subject: str, predicate: str): return 1
    def deactivate_canonical_facts(self *, book_id: str, subject: str, predicate: str): ...
    def save_canonical_fact(self, fact): ...
    def list_active_canonical_facts(self *, book_id: str): return []
    def set_assertion_status(self, assertion_id, status): ...


class FakeExtractor:
    def extract(self, *, chunk):
        start = chunk.content.index("Alice")
        end = start + len("Alice is an archivist.")
        return [ExtractedAssertion(
            statement="Alice is an archivist.",
            subject="Alice",
            predicate="occupation",
            object="archivist",
            confidence=0.99,
            start_offset=start,
            end_offset=end,
        )]


def approved_book() -> BookState:
    return BookState(
        id="book-1",
        title="Test",
        theme="Mystery",
        author_idea="Test",
        chapters=[Chapter(
            id="chapter-1",
            number=1,
            title="Discovery",
            objective="Introduce Alice",
            status=ChapterStatus.APPROVED,
            current_version=1,
        )],
    )


def test_extracts_only_approved_chapter_version_and_keeps_assertions_proposed():
    knowledge = FakeKnowledgeRepository()
    result = ExtractChapterAssertions(
        book_repository=FakeBookRepository(approved_book()),
        knowledge_repository=knowledge,
        extractor=FakeExtractor(),
    ).execute(book_id="book-1", chapter_number=1)

    assert len(result.assertions) == 1
    assert result.assertions[0].status.value == "proposed"
    assert result.assertions[0].subject == "Alice"
    assert result.evidence[0].excerpt == "Alice is an archivist."
    assert result.evidence[0].start_offset == 0
    assert result.evidence[0].end_offset == len("Alice is an archivist.")


def test_rejects_non_approved_chapter():
    book = approved_book()
    book.chapters[0].status = ChapterStatus.DRAFT

    try:
        ExtractChapterAssertions(
            book_repository=FakeBookRepository(book),
            knowledge_repository=FakeKnowledgeRepository(),
            extractor=FakeExtractor(),
        ).execute(book_id="book-1", chapter_number=1)
    except ValueError as exc:
        assert "approved chapters" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_requires_persisted_version():
    book = approved_book()
    book.chapters[0].current_version = 0

    try:
        ExtractChapterAssertions(
            book_repository=FakeBookRepository(book),
            knowledge_repository=FakeKnowledgeRepository(),
            extractor=FakeExtractor(),
        ).execute(book_id="book-1", chapter_number=1)
    except ValueError as exc:
        assert "persisted version" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
