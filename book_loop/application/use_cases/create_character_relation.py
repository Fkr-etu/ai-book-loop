from __future__ import annotations

from uuid import uuid4

from book_loop.application.ports.character_repository import CharacterRepository
from book_loop.domain.models import CharacterRelation


class CreateCharacterRelation:
    """Create a proposed typed relation between two characters in the same book."""

    def __init__(self, repository: CharacterRepository) -> None:
        self.repository = repository

    def execute(
        self,
        *,
        book_id: str,
        source_character_id: str,
        target_character_id: str,
        relation_type: str,
        assertion_ids: list[str] | None = None,
    ) -> CharacterRelation:
        source = self.repository.get_character(source_character_id)
        target = self.repository.get_character(target_character_id)
        if source.book_id != book_id or target.book_id != book_id:
            raise ValueError("Character relation endpoints must belong to the same book")

        relation = CharacterRelation(
            id=str(uuid4()),
            book_id=book_id,
            source_character_id=source_character_id,
            target_character_id=target_character_id,
            relation_type=relation_type,
            assertion_ids=assertion_ids or [],
        )
        self.repository.save_character_relation(relation)
        return relation
