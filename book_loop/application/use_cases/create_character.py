from __future__ import annotations

from uuid import uuid4

from book_loop.application.ports.character_repository import CharacterRepository
from book_loop.domain.models import Character


class CreateCharacter:
    """Create a proposed character without making any claim canonical."""

    def __init__(self, repository: CharacterRepository) -> None:
        self.repository = repository

    def execute(
        self,
        *,
        book_id: str,
        name: str,
        aliases: list[str] | None = None,
        summary: str = "",
        attributes: dict[str, str] | None = None,
        assertion_ids: list[str] | None = None,
    ) -> Character:
        character = Character(
            id=str(uuid4()),
            book_id=book_id,
            name=name,
            aliases=aliases or [],
            summary=summary,
            attributes=attributes or {},
            assertion_ids=assertion_ids or [],
        )
        self.repository.save_character(character)
        return character
