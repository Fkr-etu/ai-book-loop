from __future__ import annotations

import uuid
from typing import Any

from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

from book_loop.application.services.context import ContextBuilder
from book_loop.domain.models import BookState, Chapter, ChapterStatus, Outline, User, UserPublic
from book_loop.infrastructure.auth import (
    COOKIE_NAME,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from book_loop.infrastructure.container import Container


class RegisterPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = ""


class LoginPayload(BaseModel):
    email: EmailStr
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


class IngestDocumentPayload(BaseModel):
    name: str
    sourceType: str = "markdown"
    content: str
    metadata: dict[str, str] | None = None


class ReviewAssertionPayload(BaseModel):
    decision: str
    rationale: str = ""


def create_app(container: Container | None = None) -> FastAPI:
    if container is None:
        container = Container()

    app = FastAPI(title="AI Book Loop API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=container.settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    context_builder = ContextBuilder()

    @app.get("/health")
    def health() -> dict[str, str]:
        """Lightweight liveness endpoint for Cloud Run and load balancers."""
        return {"status": "ok"}

    def get_current_user(request: Request) -> UserPublic:
        token = request.cookies.get(COOKIE_NAME)
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.removeprefix("Bearer ")
        if not token:
            raise HTTPException(status_code=401, detail="Non authentifié.")

        payload = decode_access_token(token, secret_key=container.settings.auth_secret_key)
        if not payload or not isinstance(payload.get("sub"), str):
            raise HTTPException(status_code=401, detail="Session invalide ou expirée.")

        user = container.repository.get_user_by_id(payload["sub"])
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur introuvable.")
        return UserPublic(id=user.id, email=user.email, name=user.name)

    def set_session_cookie(response: Response, token: str) -> None:
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,
            secure=container.settings.auth_cookie_secure,
            samesite=container.settings.auth_cookie_samesite,
            path="/",
            max_age=7 * 24 * 3600,
        )

    @app.post("/api/auth/register", status_code=201)
    def register(payload: RegisterPayload, response: Response) -> dict[str, Any]:
        if container.repository.get_user_by_email(payload.email):
            raise HTTPException(status_code=400, detail="Un compte existe déjà avec cette adresse e-mail.")
        user = User(
            id=f"usr-{uuid.uuid4().hex}",
            email=payload.email,
            password_hash=hash_password(payload.password),
            name=payload.name,
        )
        created = container.repository.create_user(user)
        public = UserPublic(id=created.id, email=created.email, name=created.name)
        set_session_cookie(response, create_access_token(public, secret_key=container.settings.auth_secret_key))
        return {"user": public.model_dump(mode="json")}

    @app.post("/api/auth/login")
    def login(payload: LoginPayload, response: Response) -> dict[str, Any]:
        user = container.repository.get_user_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Adresse e-mail ou mot de passe incorrect.")
        public = UserPublic(id=user.id, email=user.email, name=user.name)
        set_session_cookie(response, create_access_token(public, secret_key=container.settings.auth_secret_key))
        return {"user": public.model_dump(mode="json")}

    @app.post("/api/auth/logout")
    def logout(response: Response) -> dict[str, Any]:
        response.delete_cookie(key=COOKIE_NAME, path="/")
        return {"message": "Déconnexion réussie."}

    @app.get("/api/auth/me")
    def me(current_user: UserPublic = Depends(get_current_user)) -> dict[str, Any]:
        return {"user": current_user.model_dump(mode="json")}

    @app.middleware("http")
    async def protect_book_routes(request: Request, call_next):
        if not request.url.path.startswith("/api/books"):
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)

        try:
            current_user = get_current_user(request)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        request.state.user = current_user
        parts = [part for part in request.url.path.split("/") if part]
        # /api/books/{book_id}/...; POST /api/books creates a new resource.
        if len(parts) >= 3:
            book_id = parts[2]
            try:
                book = container.repository.get(book_id)
            except KeyError:
                return await call_next(request)
            if book.owner_id != current_user.id:
                return JSONResponse(status_code=404, content={"detail": "Livre introuvable."})
        return await call_next(request)

    def _get_book(book_id: str) -> BookState:
        try:
            return container.repository.get(book_id)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Livre {book_id} introuvable.")

    @app.get("/api/books/{book_id}")
    def get_book(book_id: str) -> dict[str, Any]:
        return _get_book(book_id).model_dump(mode="json")

    @app.post("/api/books")
    def create_book(payload: CreateBookPayload, request: Request) -> dict[str, Any]:
        current_user: UserPublic = request.state.user
        book = container.create_book().execute(
            owner_id=current_user.id,
            title=payload.title,
            theme=payload.theme,
            author_idea=payload.author_idea,
            lore=payload.lore,
            constraints=payload.constraints,
        )
        return book.model_dump(mode="json")

    @app.put("/api/books/{book_id}")
    def update_book(book_id: str, updates: dict[str, Any] = Body(...)) -> dict[str, Any]:
        _get_book(book_id)
        try:
            updated_book = container.update_book().execute(book_id, updates)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Livre {book_id} introuvable.")
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/outline/generate")
    def generate_outline(book_id: str) -> dict[str, Any]:
        book = _get_book(book_id)
        return container.generate_outline().execute(book).model_dump(mode="json")

    @app.put("/api/books/{book_id}/outline")
    def update_outline(book_id: str, payload: UpdateOutlinePayload) -> dict[str, Any]:
        book = _get_book(book_id)
        try:
            updated_book = container.update_outline().execute(book, outline=payload.outline)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/outline/approve")
    def approve_outline(book_id: str) -> dict[str, Any]:
        book = _get_book(book_id)
        try:
            updated_book = container.approve_outline().execute(book)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/chapters")
    def add_chapter(book_id: str, payload: AddChapterPayload) -> dict[str, Any]:
        book = _get_book(book_id)
        try:
            updated_book = container.add_chapter().execute(book, chapter_number=payload.chapter_number)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/generate")
    def generate_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_book(book_id)
        try:
            state = container.generate_chapter().execute(book, chapter_number=chapter_number)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        updated_book = container.repository.get(book_id)
        return {"book": updated_book.model_dump(mode="json"), "versionNumber": state.attempt, "content": state.draft}

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/review")
    def review_chapter(book_id: str, chapter_number: int, payload: ReviewPayload = Body(default_factory=ReviewPayload)) -> dict[str, Any]:
        book = _get_book(book_id)
        try:
            updated_book, review = container.review_chapter().execute(
                book,
                chapter_number=chapter_number,
                version_number=payload.versionNumber,
                draft_text=payload.draftText,
            )
        except ValueError as exc:
            raise HTTPException(status_code=404 if "not found" in str(exc).lower() else 400, detail=str(exc))
        return {"book": updated_book.model_dump(mode="json"), "review": review.model_dump(mode="json")}

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/approve")
    def approve_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_book(book_id)
        try:
            result = container.approve_chapter_and_sync_canon().execute(
                book,
                chapter_number=chapter_number,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

        response = result.book.model_dump(mode="json")
        response["canonSync"] = {
            "sourceDocument": result.ingestion.source_document.model_dump(mode="json"),
            "assertionCount": len(result.ingestion.assertions),
            "evidenceCount": len(result.ingestion.evidence),
            "conflicts": [conflict.model_dump(mode="json") for conflict in result.conflicts],
        }
        return response

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/reject")
    def reject_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_book(book_id)
        try:
            updated_book = container.reject_chapter().execute(book, chapter_number=chapter_number)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        return updated_book.model_dump(mode="json")

    @app.get("/api/books/{book_id}/chapters/{chapter_number}/context")
    def get_canonical_context(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_book(book_id)
        chapter = next((c for c in book.chapters if c.number == chapter_number), None)
        if chapter is None:
            raise HTTPException(status_code=404, detail=f"Chapitre {chapter_number} introuvable.")
        formatted = context_builder.for_chapter(book, chapter_number)
        prev_summaries = "\n".join(
            f"Chapter {c.number} ({c.title}): {c.summary}"
            for c in book.chapters
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

    @app.post("/api/books/{book_id}/documents/ingest")
    def ingest_document(book_id: str, payload: IngestDocumentPayload) -> dict[str, Any]:
        _get_book(book_id)
        try:
            result = container.ingest_document().execute(
                book_id=book_id,
                name=payload.name,
                source_type=payload.sourceType,
                content=payload.content,
                metadata=payload.metadata,
            )
            return result.model_dump(mode="json")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.get("/api/books/{book_id}/assertions")
    def list_assertions(book_id: str) -> dict[str, Any]:
        _get_book(book_id)
        assertions = container.repository.list_assertions(book_id=book_id)
        return {"assertions": [a.model_dump(mode="json") for a in assertions]}

    @app.get("/api/books/{book_id}/conflicts")
    def list_conflicts(book_id: str) -> dict[str, Any]:
        _get_book(book_id)
        conflicts = container.repository.list_conflicts(book_id=book_id)
        return {"conflicts": [conflict.model_dump(mode="json") for conflict in conflicts]}

    @app.get("/api/books/{book_id}/canonical-facts")
    def list_canonical_facts(book_id: str) -> dict[str, Any]:
        _get_book(book_id)
        facts = container.repository.list_active_canonical_facts(book_id=book_id)
        return {"facts": [fact.model_dump(mode="json") for fact in facts]}

    @app.post("/api/books/{book_id}/assertions/{assertion_id}/review")
    def review_assertion(book_id: str, assertion_id: str, payload: ReviewAssertionPayload, request: Request) -> dict[str, Any]:
        _get_book(book_id)
        current_user: UserPublic | None = getattr(request.state, "user", None)
        reviewer_id = current_user.id if current_user else "user"
        try:
            from book_loop.domain.models import ReviewDecisionType
            decision_enum = ReviewDecisionType(payload.decision.lower())
            review = container.review_assertion().execute(
                book_id=book_id,
                assertion_id=assertion_id,
                decision=decision_enum,
                reviewer_id=reviewer_id,
                rationale=payload.rationale,
            )
            return review.model_dump(mode="json")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    return app


app = create_app()
