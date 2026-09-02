from __future__ import annotations

from book_loop.domain.models import BookState, Chapter
from book_loop.domain.protocols import BookRepository


class AddChapter:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(self, book: BookState, *, chapter_number: int) -> BookState:
        if not book.outline_approved or book.outline is None:
            raise ValueError("The author must approve the outline before adding chapters")
        if any(chapter.number == chapter_number for chapter in book.chapters):
            raise ValueError(f"Chapter {chapter_number} already exists")

        outline_chapter = next(
            (chapter for chapter in book.outline.chapters if chapter.number == chapter_number),
            None,
        )
        if outline_chapter is None:
            raise ValueError(f"Unknown chapter {chapter_number} in outline")

        book.chapters.append(
            Chapter(
                id=f"{book.id}:chapter:{chapter_number}",
                number=chapter_number,
                title=outline_chapter.title,
                objective=outline_chapter.objective,
            )
        )
        book.chapters.sort(key=lambda chapter: chapter.number)
        self.repository.save(book)
        return book
