from __future__ import annotations

import json
from typing import Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from book_loop.domain.models import BookState, Chapter, ChapterStatus, SceneReview
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
            default_book = BookState(
                id=book_id,
                title="La Porte d'Obsidienne",
                theme="Le prix de l'immortalité et la décomposition de la mémoire collective.",
                author_idea="Un archiviste amnésique découvre un manuscrit interdit gravé dans l'obsidienne.",
                lore="Dans l'Empire de Cendres, les mages utilisent l'Obsidienne stellaire pour figer les souvenirs.",
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
        book = _get_or_seed_book(book_id)
        data = book.model_dump(mode="json")
        data.update(updates)
        updated_book = BookState.model_validate(data)
        container.repository.save(updated_book)
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
        if not book.outline_approved:
            raise HTTPException(status_code=400, detail="L'outline doit être approuvé avant de générer un chapitre.")

        chapter = next((c for c in book.chapters if c.number == chapter_number), None)
        if chapter is None:
            raise HTTPException(status_code=404, detail=f"Chapitre {chapter_number} introuvable.")

        next_ver = chapter.current_version + 1
        draft_content = f"Chapitre {chapter.number}: {chapter.title}. Objectif: {chapter.objective}.\n\nDans la pénombre du scriptorium..."

        chapter.current_version = next_ver
        chapter.status = ChapterStatus.PROPOSED
        container.repository.save(book)
        container.repository.save_chapter_version(
            book_id=book.id, chapter_number=chapter.number, version=next_ver, draft=draft_content
        )

        return {
            "book": book.model_dump(mode="json"),
            "versionNumber": next_ver,
            "content": draft_content,
        }

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/review")
    def review_chapter(book_id: str, chapter_number: int, payload: ReviewPayload = Body(default_factory=ReviewPayload)) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        chapter = next((c for c in book.chapters if c.number == chapter_number), None)
        if chapter is None:
            raise HTTPException(status_code=404, detail=f"Chapitre {chapter_number} introuvable.")

        v_num = payload.versionNumber or chapter.current_version
        text = payload.draftText or f"Contenu du chapitre {chapter.number} version {v_num}"

        issues: list[str] = []
        if any(w in text.lower() for w in ["ordinateur", "robot", "telephone", "internet", "wifi"]):
            issues.append("Termes anachroniques détectés.")
        if len(text) < 10:
            issues.append("Contenu trop court.")

        approved = len(issues) == 0
        score = 9 if approved else 4

        review = SceneReview(
            score=score,
            approved=approved,
            issues=issues,
            suggestions=["Maintenir le style littéraire."] if approved else ["Réécrire sans termes anachroniques."]
        )

        container.repository.save_review(
            book_id=book.id, chapter_number=chapter.number, version=v_num, review=review
        )

        chapter.status = ChapterStatus.NEEDS_REVIEW if approved else ChapterStatus.REJECTED
        container.repository.save(book)

        return {
            "book": book.model_dump(mode="json"),
            "review": review.model_dump(mode="json")
        }

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/approve")
    def approve_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        chapter = next((c for c in book.chapters if c.number == chapter_number), None)
        if chapter is None:
            raise HTTPException(status_code=404, detail=f"Chapitre {chapter_number} introuvable.")

        chapter.status = ChapterStatus.APPROVED
        chapter.summary = f"Chapitre {chapter.number} ({chapter.title}): {chapter.objective} [Canonique]"
        container.repository.save(book)
        return book.model_dump(mode="json")

    @app.post("/api/books/{book_id}/chapters/{chapter_number}/reject")
    def reject_chapter(book_id: str, chapter_number: int) -> dict[str, Any]:
        book = _get_or_seed_book(book_id)
        chapter = next((c for c in book.chapters if c.number == chapter_number), None)
        if chapter is None:
            raise HTTPException(status_code=404, detail=f"Chapitre {chapter_number} introuvable.")

        chapter.status = ChapterStatus.REJECTED
        container.repository.save(book)
        return book.model_dump(mode="json")

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
