from __future__ import annotations

from dataclasses import dataclass

from book_loop.application.use_cases.approve_chapter import ApproveChapter
from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.application.use_cases.extract_chapter_assertions import ExtractChapterAssertions
from book_loop.domain.models import BookState, Conflict, IngestionResult
from book_loop.domain.protocols import AssertionExtractor, BookRepository, KnowledgeRepository


@dataclass(frozen=True)
class ApprovedChapterCanonSync:
    book: BookState
    ingestion: IngestionResult
    conflicts: list[Conflict]


class ApproveChapterAndSyncCanon:
    """Approve a chapter, then ingest it as proposed Canon knowledge."""

    def __init__(
        self,
        *,
        book_repository: BookRepository,
        knowledge_repository: KnowledgeRepository,
        extractor: AssertionExtractor,
    ) -> None:
        self._approve = ApproveChapter(book_repository)
        self._extract = ExtractChapterAssertions(
            book_repository=book_repository,
            knowledge_repository=knowledge_repository,
            extractor=extractor,
        )
        self._detect_conflicts = DetectConflicts(knowledge_repository)

    def execute(self, *, book: BookState, chapter_number: int) -> ApprovedChapterCanonSync:
        approved = self._approve.execute(book, chapter_number=chapter_number)
        chapter = next(chapter for chapter in approved.chapters if chapter.number == chapter_number)
        ingestion = self._extract.execute(
            book_id=approved.id,
            chapter_number=chapter_number,
            version=chapter.current_version,
        )
        conflicts = self._detect_conflicts.execute(book_id=approved.id)
        return ApprovedChapterCanonSync(
            book=approved,
            ingestion=ingestion,
            conflicts=conflicts,
        )
