import pytest
from pydantic import ValidationError

from book_loop.domain.models import Character, CharacterRelation, CharacterStatus


def test_character_keeps_identity_and_extensible_attributes_without_genre_specific_fields():
    character = Character(
        id="char-maya",
        book_id="book-1",
        name="Maya",
        aliases=["May"],
        summary="Une archiviste qui enquête sur une disparition.",
        attributes={"occupation": "archiviste", "fear": "être suivie"},
        assertion_ids=["assertion-1"],
    )

    assert character.status is CharacterStatus.PROPOSED
    assert character.attributes["occupation"] == "archiviste"
    assert character.assertion_ids == ["assertion-1"]


def test_character_requires_a_name():
    with pytest.raises(ValidationError):
        Character(id="char-1", book_id="book-1", name="")


def test_character_relation_is_typed_and_traceable_to_assertions():
    relation = CharacterRelation(
        id="rel-1",
        book_id="book-1",
        source_character_id="char-maya",
        target_character_id="char-leo",
        relation_type="suspects",
        assertion_ids=["assertion-42"],
    )

    assert relation.relation_type == "suspects"
    assert relation.status is CharacterStatus.PROPOSED
    assert relation.assertion_ids == ["assertion-42"]


def test_character_relation_cannot_connect_character_to_itself():
    with pytest.raises(ValidationError, match="distinct characters"):
        CharacterRelation(
            id="rel-1",
            book_id="book-1",
            source_character_id="char-maya",
            target_character_id="char-maya",
            relation_type="knows",
        )


def test_character_relation_requires_a_type():
    with pytest.raises(ValidationError):
        CharacterRelation(
            id="rel-1",
            book_id="book-1",
            source_character_id="char-maya",
            target_character_id="char-leo",
            relation_type="",
        )
