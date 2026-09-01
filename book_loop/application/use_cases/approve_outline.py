from __future__ import annotations

from book_loop.domain.models import BookState
from book_loop.domain.protocols import BookRepository


class ApproveOutline:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(self, book: BookState) -> BookState:
        if not book.outline:
            raise ValueError("Cannot approve an outline that has not been generated")
        book.outline_approved = True
        self.repository.save(book)
        return book
