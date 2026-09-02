from __future__ import annotations

import uuid
from typing import Any
from fastapi import FastAPI, HTTPException, Body, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

from book_loop.domain.models import BookState, Chapter, ChapterStatus, User, User Public, Outline

from book_loop.infrastructure.container import Container
from book_loop.infrastructure.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    COOKIE_NAME,
)
from book_loop.application.services.context import ContextBuilder


class RegisterPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = ""


class LoginPayload(BaseModel):
    email: str
    password: str


class CreateBookPayload(BaseModel):
    title: str
    theme: str
    author_idea: str
    lore: str = ""
    constraints: list[str] = Field(default_factory=list)


class AddChapterPayload(BaseModel):
    chapter_number: int = Field(gt=0)


class ReviewPayload(BaseModel):
    versionNumber: int | None = None
    draftText: str | None = None


class UpdateOutlinePayload(BaseModel):
    outline: Outline


def create_app(container: Container | None = None) -> FastAPI:
    if container is None:
        container = Container()

    app = FastAPI(title="AI Book Loop API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    context_builder = ContextBuilder()

    def get_current_user(request: Request) -> UserPublic:
        token = request.cookies.get(COOKIE_NAME)
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.removeprefix("Bearer ")

        if not token:
            raise HTTPException(status_code=401, detail="Non authentifié.")

        payload = decode_access_token(token)
        if not payload or "sub" not in payload:
            raise HTTPException(status_code=401, detail="Session invalide ou expirée.")

        user = container.repository.get_user_by_id(payload["sub"])
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur introuvable.")

        return UserPublic(id=user.id, email=user.email, name=user.name)

    @app.post("/api/auth/register", status_code=201)
    def register(payload: RegisterPayload, response: Response) -> dict[str, Any]:
        existing_user = container.repository.get_user_by_email(payload.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Un compte existe déjà avec cette adresse e-mail.")

        user_id = f"usr-{uuid.uuid4().hex[:8]}"
        hashed = hash_password(payload.password)
        new_user = User(
            id=user_id,
            email=payload.email,
            password_hash=hashed,
            name=payload.name,
        )
        created = container.repository.create_user(new_user)
        user_public = UserPublic(id=created.id, email=created.email, name=created.name)

        token = create_access_token(user_public)
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,
            secure=False,  # Set to True in HTTPS production environments
            samesite="lax",
            path="/",
            max_age=7 * 24 * 3600,
        )
        return {"user": user_public.model_dump(mode="json")}

    @app.post("/api/auth/login")
    def login(payload: LoginPayload, response: Response) -> dict[str, Any]:
        user = container.repository.get_user_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Adresse e-mail ou mot de passe incorrect.")

        user_public = UserPublic(id=user.id, email=user.email, name=user.name)
        token = create_access_token(user_public)
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
            max_age=7 * 24 * 3600,
        )
        return {"user": user_public.model_dump(mode="json")}

    @app.post("/api/auth/logout")
    def logout(response: Response) -> dict[str, Any]:
        response.delete_cookie(key=COOKIE_NAME, path="/", samesite="lax")
        return {"message": "Déconnexion réussie."}

    @app.get("/api/auth/me")
    def me(current_user: UserPublic = Depends(get_current_user)) -> dict[str, Any]:
        return {"user": current_user.model_dump(mode="json")}

    def _get_or_seed_book(book_id: str) -> BookState:
        try:
            return container.repository.get(book_id)
        except KeyError:
            if book_id != "proj-001":
                raise HTTPException(status_code=404, detail=f"Livre {book_id} introuvable.")

            default_book = BookState(
                id="proj-001",
                title="L'Écho du Codex",
                theme="Mystères alchimiques et cités perdues",
                author_idea="Une chercheuse découvre un grimoire mécanique dont chaque page modifie la mémoire de son lecteur.",
                lore="Dans l'archipel d'Aethelgard, les parchemins sont animés par une poussière stellaire pour figer les souvenirs.",
                constraints=[
                    "Interdire les anachronismes modernes",
                    "Conserver une voix narrative érudite à la 3ème personne",
                    "Maintenir des descriptions tactiles"
                ],
                outline=Outline(chapters=[
                    {"number": 1, "title": "Le Murmure du Parchemin", "objective": "Découvrir la tablette d'obsidienne dans les archives scellées."},
                    {"number": 2, "title": "La Cité Suspendue", "objective": "Ascension des tours mnésiques jusqu'au pont de verre."},
                    {"number": 3, "title": "L'Éclipse du Codex", "objective": "Affronter le sacrifice final et révéler le secret du codex."},
                ]),
                outline_approved=True,
                chapters=[
                    Chapter(
                        id="chap-1", number=1, title="Le Murmure du Parchemin",
                        objective="Découvrir la tablette d'obsidienne dans les archives scellées.",
                        status=ChapterStatus.APPROVED, current_version=1,
                        summary="Chapitre 1: Découverte de la tablette d'obsidienne [Canonique]"
                    ),
                    Chapter(
                        id="chap-2", number=2, title="La Cité Suspendue",
                        objective="Ascension des tours mnésiques jusqu'au pont de verre.",
                        status=ChapterStatus.NEEDS_REVIEW, current_version=1, summary=""
                    )
                ]
            )
            container.repository.save(default_book)
            return default_book

    @app.get("/api/books/{book_id}")
    def get_book(book_id: str) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        return book.model_dump(mode="json")

    @app.post("/api/books")
    def create_book(payload: CreateBookPayload) -> dict[str, Any]:
        book = container.create_book().execute(
            title=payload.title, theme=payload.theme, author_idea=payload.author_idea,
            lore=payload.lore, constraints=payload.constraints,
        )
        return book.model_dump(mode="json")

    @app.put("/api/books/{book_id}")
    def update_book(book_id: str, updates: dict[str, Any] = Body(...)) -> dict[str, Any]:
        _get_or_seed_book(book_id)
        try:
            updated_book = container.update_book().execute(book_id, updates)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Livre {book_id} introuvable.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/outline/generate")
    def generate_outline(book_id: str) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        updated_book = container.generate_outline().execute(book)
        return updated_book.model_dump(mode="json")

    @app.put("/api/books/{book_id}/outline")
    def update_outline(book_id: str, payload: UpdateOutlinePayload) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        try:
            updated_book = container.update_outline().execute(book, outline=payload.outline)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/outline/approve")
    def approve_outline(book_id: str) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        try:
            updated_book = container.approve_outline().execute(book)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/chapters")
    def add_chapter(book_id: str, payload: AddChapterPayload) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        try:
            updated_book = container.add_chapter().execute(book, chapter_number=payload.chapter_number)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/generate")
    def generate_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        try:
            state = container.generate_chapter().execute(book, chapter_number=chapter_number)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        updated_book = container.repository.get(book_id)
        return {"book": updated_book.model_dump(mode="json"), "versionNumber": state.attempt, "content": state.draft}

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/review")
    def review_chapter(book_id: str, chapter_number: int, payload: ReviewPayload = Body(default_factory=ReviewPayload)) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        try:
            updated_book, review = container.review_chapter().execute(
                book, chapter_number=chapter_number, version_number=payload.versionNumber, draft_text=payload.draftText
            )
        except ValueError as e:
            raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))
        return {"book": updated_book.model_dump(mode="json"), "review": review.model_dump(mode="json")}

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/approve")
    def approve_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        try:
            updated_book = container.approve_chapter().execute(book, chapter_number=chapter_number)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/reject")
    def reject_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        try:
            updated_book = container.reject_chapter().execute(book, chapter_number=chapter_number)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return updated_book.model_dump(mode="json")

    @app.get("/api/books/{book_id}/chapters/{chapter_number}/context")
    def get_canonical_context(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        chapter = next((c for c in book.chapters if c.number == chapter_number), None)
        if chapter is None:
            raise HTTPException(status_code=404, detail=f"Chapitre {chapter_number} introuvable.")
        formatted = context_builder.for_chapter(book, chapter_number)
        prev_summaries = "\n".join(
            f"Chapter {c.number} ({c.title}): {c.summary}" for c in book.chapters
            if c.number < chapter_number and c.summary
        )
        return {
            "authorIdea": book.author_idea,
            "theme": book.theme,
            "lore": book.lore,
            "globalOutline": book.outline.model_dump(mode="json") if book.outline else None,
            "constraints": book.constraints,
            "previousSummaries": prev_summaries,
            "currentObjective": chapter.objective,
            "formattedContext": formatted,
        }

    return app


app = create_app()
