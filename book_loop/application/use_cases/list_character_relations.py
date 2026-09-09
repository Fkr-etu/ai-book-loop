from __future__ import annotations

from book_loop.application.ports.character_repository import CharacterRepository
from book_loop.domain.models import CharacterRelation


class ListCharacterRelations:
    def __init__(self, repository: CharacterRepository) -> None:
        self._repository = repository

    def execute(self, *, book_id: str) -> list[CharacterRelation]:
        return self._repository.list_character_relations(book_id=book_id)
