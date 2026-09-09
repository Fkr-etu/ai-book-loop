from __future__ import annotations

import pytest

from book_loop.application.use_cases.create_character import CreateCharacter
from book_loop.application.use_cases.create_character_relation import CreateCharacterRelation
from book_loop.application.use_cases.update_character import UpdateCharacter
from book_loop.domain.models import Character


class FakeCharacterRepository:
    def __init__(self) -> None:
        self.characters: dict[str, Character] = {}
        self.relations = []

    def save_character(self, character: Character) -> None:
        self.characters[character.id] = character

    def get_character(self, character_id: str) -> Character:
        if character_id not in self.characters:
            raise KeyError(character_id)
        return self.characters[character_id]

    def list_characters(self, *, book_id: str) -> list[Character]:
        return [c for c in self.characters.values() if c.book_id == book_id]

    def delete_character(self, character_id: str) -> None:
        if character_id not in self.characters:
            raise KeyError(character_id)
        del self.characters[character_id]

    def save_character_relation(self, relation) -> None:
        self.relations.append(relation)

    def get_character_relation(self, relation_id: str):
        return next(r for r in self.relations if r.id == relation_id)

    def list_character_relations(self, *, book_id: str):
        return [r for r in self.relations if r.book_id == book_id]

    def delete_character_relation(self, relation_id: str) -> None:
        self.relations = [r for r in self.relations if r.id != relation_id]


def test_create_character_starts_as_proposed_and_persists_through_port():
    repository = FakeCharacterRepository()

    character = CreateCharacter(repository).execute(
        book_id="book-1",
        name="Maya",
        attributes={"occupation": "archiviste"},
        assertion_ids=["assertion-1"],
    )

    assert character.status.value == "proposed"
    assert repository.characters[character.id] == character


def test_update_character_cannot_move_it_to_another_book():
    repository = FakeCharacterRepository()
    character = CreateCharacter(repository).execute(book_id="book-1", name="Maya")

    with pytest.raises(ValueError, match="book_id"):
        UpdateCharacter(repository).execute(character.id, {"book_id": "book-2"})


def test_update_character_revalidates_the_domain_model():
    repository = FakeCharacterRepository()
    character = CreateCharacter(repository).execute(book_id="book-1", name="Maya")

    updated = UpdateCharacter(repository).execute(
        character.id,
        {"summary": "Une archiviste.", "attributes": {"role": "enquêtrice"}},
    )

    assert updated.summary == "Une archiviste."
    assert updated.attributes == {"role": "enquêtrice"}


def test_create_relation_requires_both_endpoints_to_belong_to_book():
    repository = FakeCharacterRepository()
    maya = CreateCharacter(repository).execute(book_id="book-1", name="Maya")
    leo = CreateCharacter(repository).execute(book_id="book-2", name="Leo")

    with pytest.raises(ValueError, match="same book"):
        CreateCharacterRelation(repository).execute(
            book_id="book-1",
            source_character_id=maya.id,
            target_character_id=leo.id,
            relation_type="suspects",
        )


def test_create_relation_persists_a_proposed_typed_relation():
    repository = FakeCharacterRepository()
    maya = CreateCharacter(repository).execute(book_id="book-1", name="Maya")
    leo = CreateCharacter(repository).execute(book_id="book-1", name="Leo")

    relation = CreateCharacterRelation(repository).execute(
        book_id="book-1",
        source_character_id=maya.id,
        target_character_id=leo.id,
        relation_type="suspects",
        assertion_ids=["assertion-42"],
    )

    assert relation.status.value == "proposed"
    assert relation.relation_type == "suspects"
    assert relation.assertion_ids == ["assertion-42"]
    assert repository.relations == [relation]
