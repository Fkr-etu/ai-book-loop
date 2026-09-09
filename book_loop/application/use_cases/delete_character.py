from __future__ import annotations

from book_loop.application.ports.character_repository import CharacterRepository


class DeleteCharacter:
    def __init__(self, repository: CharacterRepository) -> None:
        self.repository = repository

    def execute(self, character_id: str) -> None:
        self.repository.delete_character(character_id)
