from __future__ import annotations

from book_loop.domain.models import BookState, ChapterStatus
from book_loop.domain.protocols import BookRepository


class ApproveChapter:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(self, book: BookState, chapter_number: int) -> BookState:
        chapter = next((c for c in book.chapters if c.number == chapter_number), None)
        if chapter is None:
            raise ValueError(f"Chapter {chapter_number} not found")

        chapter.status = ChapterStatus.APPROVED
        chapter.summary = f"Chapitre {chapter.number} ({chapter.title}): {chapter.objective} [Canonique]"
        self.repository.save(book)
        return book
