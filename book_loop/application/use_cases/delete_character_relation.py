from __future__ import annotations

from book_loop.application.ports.character_repository import CharacterRepository


class DeleteCharacterRelation:
    def __init__(self, repository: CharacterRepository) -> None:
        self.repository = repository

    def execute(self, relation_id: str) -> None:
        self.repository.delete_character_relation(relation_id)
