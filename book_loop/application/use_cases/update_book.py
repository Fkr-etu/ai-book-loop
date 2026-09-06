from __future__ import annotations

from typing import Any

from book_loop.domain.models import BookState
from book_loop.domain.protocols import BookRepository


class UpdateBook:
    _IMMUTABLE_FIELDS = frozenset({"id", "owner_id"})

    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def execute(self, book_id: str, updates: dict[str, Any]) -> BookState:
        forbidden = self._IMMUTABLE_FIELDS.intersection(updates)
        if forbidden:
            fields = ", ".join(sorted(forbidden))
            raise ValueError(f"Cannot update immutable book field(s): {fields}")

        book = self.repository.get(book_id)
        data = book.model_dump(mode="json")
        data.update(updates)
        updated_book = BookState.model_validate(data)
        self.repository.save(updated_book)
        return updated_book
