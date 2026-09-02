from __future__ import annotations

from book_loop.domain.models import BookState, Chapter
from book_loop.domain.protocols import BookRepository


class AddChapter:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(self, book: BookState, *, title: str, objective: str) -> BookState:
        if not book.outline_approved:
            raise ValueError("The author must approve the outline before adding chapters")
        number = len(book.chapters) + 1
        book.chapters.append(
            Chapter(id=f"{book.id}:chapter:{number}", number=number, title=title, objective=objective)
        )
        self.repository.save(book)
        return book
