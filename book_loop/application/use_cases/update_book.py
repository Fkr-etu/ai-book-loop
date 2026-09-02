from __future__ import annotations

from typing import Any
from book_loop.domain.models import BookState
from book_loop.domain.protocols import BookRepository


class UpdateBook:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(self, book_id: str, updates: dict[str, Any]) -> BookState:
        book = self.repository.get(book_id)
        data = book.model_dump(mode="json")
        data.update(updates)
        updated_book = BookState.model_validate(data)
        self.repository.save(updated_book)
        return updated_book
