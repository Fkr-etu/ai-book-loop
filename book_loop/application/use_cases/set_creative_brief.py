from __future__ import annotations

from book_loop.domain.models import BookState, CreativeBrief
from book_loop.domain.protocols import BookRepository


class SetCreativeBrief:
    """Persist the author's structured creative brief without involving an LLM."""

    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(self, book: BookState, brief: CreativeBrief) -> BookState:
        book.creative_brief = brief
        self.repository.save(book)
        return book
