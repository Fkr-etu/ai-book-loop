from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from book_loop.api.dependencies import get_container, get_owned_book
from book_loop.domain.models import Character
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books/{book_id}/characters", tags=["characters"])


class CharacterCreatePayload(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)
    summary: str = ""
    attributes: dict[str, Any] = Field(default_factory=dict)
    assertion_ids: list[str] = Field(default_factory=list)


class CharacterUpdatePayload(BaseModel):
    name: str | None = None
    aliases: list[str] | None = None
    summary: str | None = None
    attributes: dict[str, Any] | None = None
    status: str | None = None
    assertion_ids: list[str] | None = None


class CharacterRelationCreatePayload(BaseModel):
    target_character_id: str
    relation_type: str
    assertion_ids: list[str] = Field(default_factory=list)


def _book(book_id: str, request: Request, container: Container):
    return get_owned_book(book_id, request, container)


@router.get("", response_model=list[Character])
def list_characters(book_id: str, request: Request, container: Container = Depends(get_container)) -> list[Character]:
    book = _book(book_id, request, container)
    return container.list_characters().execute(book_id=book.id)


@router.post("", response_model=Character, status_code=201)
def create_character(book_id: str, payload: CharacterCreatePayload, request: Request, container: Container = Depends(get_container)) -> Character:
    book = _book(book_id, request, container)
    return container.create_character().execute(
        book_id=book.id,
        name=payload.name,
        aliases=payload.aliases,
        summary=payload.summary,
        attributes=payload.attributes,
        assertion_ids=payload.assertion_ids,
    )


@router.get("/{character_id}", response_model=Character)
def get_character(book_id: str, character_id: str, request: Request, container: Container = Depends(get_container)) -> Character:
    book = _book(book_id, request, container)
    try:
        character = container.get_character().execute(character_id=character_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    if character.book_id != book.id:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    return character


@router.put("/{character_id}", response_model=Character)
def update_character(book_id: str, character_id: str, payload: CharacterUpdatePayload, request: Request, container: Container = Depends(get_container)) -> Character:
    book = _book(book_id, request, container)
    updates = payload.model_dump(exclude_unset=True)
    try:
        character = container.get_character().execute(character_id=character_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    if character.book_id != book.id:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    try:
        return container.update_character().execute(character_id=character_id, updates=updates)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/{character_id}", status_code=204)
def delete_character(book_id: str, character_id: str, request: Request, container: Container = Depends(get_container)) -> None:
    book = _book(book_id, request, container)
    try:
        character = container.get_character().execute(character_id=character_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    if character.book_id != book.id:
        raise HTTPException(status_code=404, detail="Personnage introuvable.")
    container.delete_character().execute(character_id=character_id)


@router.get("/relations", response_model=list[Any])
def list_relations(book_id: str, request: Request, container: Container = Depends(get_container)) -> list[Any]:
    book = _book(book_id, request, container)
    return container.list_character_relations().execute(book_id=book.id)


@router.post("/{character_id}/relations", response_model=Any, status_code=201)
def create_relation(book_id: str, character_id: str, payload: CharacterRelationCreatePayload, request: Request, container: Container = Depends(get_container)) -> Any:
    book = _book(book_id, request, container)
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
def delete_relation(book_id: str, relation_id: str, request: Request, container: Container = Depends(get_container)) -> None:
    book = _book(book_id, request, container)
    try:
        relation = container.get_character_relation().execute(relation_id=relation_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Relation introuvable.")
    if relation.book_id != book.id:
        raise HTTPException(status_code=404, detail="Relation introuvable.")
    container.delete_character_relation().execute(relation_id=relation_id)
