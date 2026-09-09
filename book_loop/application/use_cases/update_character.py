from __future__ import annotations

from typing import Any

from book_loop.application.ports.character_repository import CharacterRepository
from book_loop.domain.models import Character


class UpdateCharacter:
    _IMMUTABLE_FIELDS = frozenset({"id", "book_id"})

    def __init__(self, repository: CharacterRepository) -> None:
        self.repository = repository

    def execute(self, character_id: str, updates: dict[str, Any]) -> Character:
        forbidden = self._IMMUTABLE_FIELDS.intersection(updates)
        if forbidden:
            fields = ", ".join(sorted(forbidden))
            raise ValueError(f"Cannot update immutable character field(s): {fields}")

        character = self.repository.get_character(character_id)
        data = character.model_dump(mode="json")
        data.update(updates)
        updated = Character.model_validate(data)
        self.repository.save_character(updated)
        return updated
