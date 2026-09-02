from __future__ import annotations

from book_loop.domain.models import BookState
from book_loop.domain.protocols import BookRepository


class UpdateOutline:
    """Replace the author's editable outline and invalidate prior approval."""

    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(self, book: BookState, *, outline: str) -> BookState:
        if not outline.strip():
            raise ValueError("The outline cannot be empty")

        book.outline = outline
        book.outline_approved = False
        self.repository.save(book)
        return book
