from __future__ import annotations

from book_loop.application.ports.character_repository import CharacterRepository
from book_loop.domain.models import Character


class GetCharacter:
    def __init__(self, repository: CharacterRepository) -> None:
        self._repository = repository

    def execute(self, *, character_id: str) -> Character:
        return self._repository.get_character(character_id)
