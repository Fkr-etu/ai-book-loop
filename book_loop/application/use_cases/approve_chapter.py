from __future__ import annotations

from book_loop.domain.models import BookState, ChapterStatus
from book_loop.domain.protocols import BookRepository


class ApproveChapter:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(self, book: BookState, chapter_number: int, version_number: int | None = None) -> BookState:
        chapter = next((c for c in book.chapters if c.number == chapter_number), None)
        if chapter is None:
            raise ValueError(f"Chapter {chapter_number} not found")
        if chapter.status != ChapterStatus.NEEDS_REVIEW:
            raise ValueError(f"Chapter {chapter_number} must be reviewed before approval")

        version = version_number or chapter.reviewed_version
        if version is None or version <= 0:
            raise ValueError(f"Chapter {chapter_number} has no reviewed version to approve")
        if chapter.reviewed_version != version:
            raise ValueError(f"Chapter {chapter_number} version {version} has not been reviewed")
        self.repository.get_chapter_version(book.id, chapter_number, version)
        chapter.current_version = version
        chapter.status = ChapterStatus.APPROVED
        chapter.summary = f"Chapitre {chapter.number} ({chapter.title}): {chapter.objective} [Canonique]"
        self.repository.save(book)
        return book
