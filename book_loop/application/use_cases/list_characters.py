from __future__ import annotations

from book_loop.application.ports.character_repository import CharacterRepository
from book_loop.domain.models import Character


class ListCharacters:
    def __init__(self, repository: CharacterRepository) -> None:
        self._repository = repository

    def execute(self, *, book_id: str) -> list[Character]:
        return self._repository.list_characters(book_id=book_id)
