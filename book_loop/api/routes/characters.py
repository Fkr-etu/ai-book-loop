from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from book_loop.api.dependencies import get_container, get_owned_book
from book_loop.domain.models import BookState, Character, CharacterRelation
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books/{book_id}/characters", tags=["characters"])


class CharacterCreatePayload(BaseModel):
    name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    summary: str = ""
    attributes: dict[str, str] = Field(default_factory=dict)
    assertion_ids: list[str] = Field(default_factory=list)


class CharacterUpdatePayload(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    aliases: list[str] | None = None
    summary: str | None = None
    attributes: dict[str, str] | None = None
    status: str | None = None
    assertion_ids: list[str] | None = None


class CharacterRelationCreatePayload(BaseModel):
    target_character_id: str
    relation_type: str = Field(min_length=1)
    assertion_ids: list[str] = Field(default_factory=list)


@router.get("", response_model=list[Character])
def list_characters(book: BookState = Depends(get_owned_book), container: Container = Depends(get_container)) -> list[Character]:
    return container.list_characters().execute(book_id=book.id)


@router.post("", response_model=Character, status_code=201)
def create_character(payload: CharacterCreatePayload, book: BookState = Depends(get_owned_book), container: Container = Depends(get_container)) -> Character:
    return container.create_character().execute(
        book_id=book.id,
        name=payload.name,
        aliases=payload.aliases,
        summary=payload.summary,
        attributes=payload.attributes,
        assertion_ids=payload.assertion_ids,
    )


@router.get("/relations", response_model=list[CharacterRelation])
def list_relations(book: BookState = Depends(get_owned_book), container: Container = Depends(get_container)) -> list[CharacterRelation]:
    return container.list_character_relations().execute(book_id=book.id)


@router.post("/{character_id}/relations", response_model=CharacterRelation, status_code=201)
def create_relation(character_id: str, payload: CharacterRelationCreatePayload, book: BookState = Depends(get_owned_book), container: Container = Depends(get_container)) -> CharacterRelation:
    try:
        return container.create_character_relation().execute(
            book_id=book.id,
            source_character_id=character_id,
            target_character_id=payload.target_character_id,
            relation_type=payload.relation_type,
            assertion_ids=payload.assertion_ids,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/relations/{relation_id}", status_code=204)
def delete_relation(relation_id: str, book: BookState = Depends(get_owned_book), container: Container = Depends(get_container)) -> None:
    relations = container.list_character_relations().execute(book_id=book.id)
    if not any(relation.id == relation_id for relation in relations):
        raise HTTPException(status_code=404, detail="Relation introuvable.")
    container.delete_character_relation().execute(relation_id=relation_id)


@router.get("/{character_id}", response_model=Character)
def get_character(character_id: str, book: BookState = Depends(get_owned_book), container: Container = Depends(get_container)) -> Character:
    try:
        character = container.get_character().execute(character_id=character_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    if character.book_id != book.id:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    return character


@router.put("/{character_id}", response_model=Character)
def update_character(character_id: str, payload: CharacterUpdatePayload, book: BookState = Depends(get_owned_book), container: Container = Depends(get_container)) -> Character:
    updates = payload.model_dump(exclude_unset=True)
    try:
        character = container.get_character().execute(character_id=character_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    if character.book_id != book.id:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    try:
        return container.update_character().execute(character_id=character_id, **updates)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/{character_id}", status_code=204)
def delete_character(character_id: str, book: BookState = Depends(get_owned_book), container: Container = Depends(get_container)) -> None:
    try:
        character = container.get_character().execute(character_id=character_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    if character.book_id != book.id:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    container.delete_character().execute(character_id=character_id)
