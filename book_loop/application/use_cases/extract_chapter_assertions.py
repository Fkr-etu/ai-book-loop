from __future__ import annotations

from book_loop.domain.models import IngestionResult
from book_loop.domain.protocols import AssertionExtractor, BookRepository, KnowledgeRepository
from book_loop.application.use_cases.ingest_document import IngestDocument


class ExtractChapterAssertions:
    """Ingest an approved chapter version into the knowledge layer as proposed assertions."""

    def __init__(
        self,
        *,
        book_repository: BookRepository,
        knowledge_repository: KnowledgeRepository,
        extractor: AssertionExtractor,
        chunk_size: int = 1800,
    ) -> None:
        self._books = book_repository
        self._knowledge = knowledge_repository
        self._ingest = IngestDocument(
            repository=knowledge_repository,
            extractor=extractor,
            chunk_size=chunk_size,
        )

    def execute(self, *, book_id: str, chapter_number: int, version: int | None = None) -> IngestionResult:
        book = self._books.get(book_id)
        chapter = next((item for item in book.chapters if item.number == chapter_number), None)
        if chapter is None:
            raise KeyError(f"Unknown chapter: {chapter_number}")
        if chapter.status.value != "approved":
            raise ValueError("Only approved chapters can be added to the Canon knowledge layer")

        selected_version = version if version is not None else chapter.current_version
        if selected_version < 1:
            raise ValueError("An approved chapter must have a persisted version")
        draft = self._books.get_chapter_version(book_id, chapter_number, selected_version)
        return self._ingest.execute(
            book_id=book_id,
            name=f"Chapter {chapter_number}: {chapter.title} v{selected_version}",
            source_type="approved_chapter",
            content=draft,
            metadata={
                "chapter_number": str(chapter_number),
                "chapter_version": str(selected_version),
            },
        )
