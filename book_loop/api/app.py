from __future__ import annotations

from typing import Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from book_loop.domain.models import BookState, Chapter, ChapterStatus
from book_loop.infrastructure.container import Container
from book_loop.application.services.context import ContextBuilder


class CreateBookPayload(BaseModel):
    title: str
    theme: str
    author_idea: str
    lore: str = ""
    constraints: list[str] = Field(default_factory=list)


class AddChapterPayload(BaseModel):
    title: str
    objective: str


class ReviewPayload(BaseModel):
    versionNumber: int | None = None
    draftText: str | None = None


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
                outline="1. Le Murmure du Parchemin\n2. La Cité Suspendue\n3. L'Éclipse du Codex",
                outline_approved=True,
                chapters=[
                    Chapter(
                        id="chap-1",
                        number=1,
                        title="Le Murmure du Parchemin",
                        objective="Découvrir la tablette d'obsidienne dans les archives scellées.",
                        status=ChapterStatus.APPROVED,
                        current_version=1,
                        summary="Chapitre 1: Découverte de la tablette d'obsidienne [Canonique]"
                    ),
                    Chapter(
                        id="chap-2",
                        number=2,
                        title="La Cité Suspendue",
                        objective="Ascension des tours mnésiques jusqu'au pont de verre.",
                        status=ChapterStatus.NEEDS_REVIEW,
                        current_version=1,
                        summary=""
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
        use_case = container.create_book()
        book = use_case.execute(
            title=payload.title,
            theme=payload.theme,
            author_idea=payload.author_idea,
            lore=payload.lore,
            constraints=payload.constraints,
        )
        return book.model_dump(mode="json")

    @app.put("/api/books/{book_id}")
    def update_book(book_id: str, updates: dict[str, Any] = Body(...)) -> dict[str, Any]:
        _get_or_seed_book(book_id)
        use_case = container.update_book()
        try:
            updated_book = use_case.execute(book_id, updates)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Livre {book_id} introuvable.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/outline/generate")
    def generate_outline(book_id: str) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        use_case = container.generate_outline()
        updated_book = use_case.execute(book)
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/outline/approve")
    def approve_outline(book_id: str) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        use_case = container.approve_outline()
        try:
            updated_book = use_case.execute(book)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/chapters")
    def add_chapter(book_id: str, payload: AddChapterPayload) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        use_case = container.add_chapter()
        try:
            updated_book = use_case.execute(
                book, title=payload.title, objective=payload.objective
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/generate")
    def generate_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        use_case = container.generate_chapter()
        try:
            state = use_case.execute(book, chapter_number=chapter_number)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        updated_book = container.repository.get(book_id)
        return {
            "book": updated_book.model_dump(mode="json"),
            "versionNumber": state.attempt,
            "content": state.draft,
        }

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/review")
    def review_chapter(
        book_id: str,
        chapter_number: int,
        payload: ReviewPayload = Body(default_factory=ReviewPayload),
    ) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        use_case = container.review_chapter()
        try:
            updated_book, review = use_case.execute(
                book,
                chapter_number=chapter_number,
                version_number=payload.versionNumber,
                draft_text=payload.draftText,
            )
        except ValueError as e:
            raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))

        return {
            "book": updated_book.model_dump(mode="json"),
            "review": review.model_dump(mode="json"),
        }

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/approve")
    def approve_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        use_case = container.approve_chapter()
        try:
            updated_book = use_case.execute(book, chapter_number=chapter_number)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return updated_book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/reject")
    def reject_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        use_case = container.reject_chapter()
        try:
            updated_book = use_case.execute(book, chapter_number=chapter_number)
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
        if isinstance(formatted, str):
            formatted_text = formatted
        elif hasattr(formatted, "formatted"):
            formatted_text = str(formatted.formatted)
        elif hasattr(formatted, "author_idea"):
            constraints = getattr(formatted, "constraints", [])
            constraints_str = "\n".join(f"- {c}" for c in constraints) if isinstance(constraints, list) else str(constraints)
            formatted_text = (
                f"AUTHOR IDEA:\n{getattr(formatted, 'author_idea', '')}\n\n"
                f"THEME:\n{getattr(formatted, 'theme', '')}\n\n"
                f"LORE:\n{getattr(formatted, 'lore', '')}\n\n"
                f"GLOBAL OUTLINE:\n{getattr(formatted, 'outline', '')}\n\n"
                f"CONSTRAINTS:\n{constraints_str}\n\n"
                f"PREVIOUS CHAPTER SUMMARIES:\n{getattr(formatted, 'previous_summaries', '')}\n\n"
                f"CURRENT CHAPTER OBJECTIVE:\n{getattr(formatted, 'chapter_objective', '')}"
            )
        elif isinstance(formatted, dict):
            formatted_text = "\n\n".join(
                f"{k.upper().replace('_', ' ')}:\n{v}" for k, v in formatted.items()
            )
        else:
            formatted_text = str(formatted)

        prev_summaries = "\n".join(
            f"Chapter {c.number} ({c.title}): {c.summary}"
            for c in book.chapters
            if c.number < chapter_number and c.summary
        )

        return {
            "authorIdea": book.author_idea,
            "theme": book.theme,
            "lore": book.lore,
            "globalOutline": book.outline or "",
            "constraints": book.constraints,
            "previousSummaries": prev_summaries,
            "currentObjective": chapter.objective,
            "formattedContext": formatted_text,
        }

    return app


app = create_app()
