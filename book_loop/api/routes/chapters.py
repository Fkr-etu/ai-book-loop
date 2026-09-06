from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field

from book_loop.api.dependencies import get_book, get_container
from book_loop.application.services.context import ContextBuilder
from book_loop.domain.workflow import ChapterWorkflowRun
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books/{book_id}/chapters", tags=["chapters"])
context_builder = ContextBuilder()


class AddChapterPayload(BaseModel):
    chapter_number: int = Field(gt=0)


class ReviewPayload(BaseModel):
    versionNumber: int | None = None
    draftText: str | None = None


def _workflow_run_payload(run: ChapterWorkflowRun) -> dict[str, Any]:
    return run.model_dump(mode="json")


@router.post("")
def add_chapter(book_id: str, payload: AddChapterPayload, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_book(book_id, container)
    try:
        updated_book = container.add_chapter().execute(book, chapter_number=payload.chapter_number)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return updated_book.model_dump(mode="json")


@router.post("/{chapter_number}/generate")
def generate_chapter(book_id: str, chapter_number: int, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_book(book_id, container)
    try:
        state = container.generate_chapter().execute(book, chapter_number=chapter_number)
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    updated_book = container.repository.get(book_id)
    try:
        run = container.workflow_store.get(state.workflow_run_id)
    except KeyError:
        raise HTTPException(status_code=500, detail="Workflow run introuvable après génération.")
    return {
        "book": updated_book.model_dump(mode="json"),
        "versionNumber": state.attempt,
        "content": state.draft,
        "workflowRun": _workflow_run_payload(run),
    }


@router.get("/{chapter_number}/workflow-run")
def get_latest_workflow_run(book_id: str, chapter_number: int, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_book(book_id, container)
    try:
        run = container.workflow_store.get_latest(book_id=book_id, chapter_number=chapter_number)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Aucun workflow pour le chapitre {chapter_number}.")
    return _workflow_run_payload(run)


@router.get("/{chapter_number}/workflow-runs/{run_id}")
def get_workflow_run(book_id: str, chapter_number: int, run_id: str, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_book(book_id, container)
    try:
        run = container.workflow_store.get(run_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow introuvable.")
    if run.book_id != book_id or run.chapter_number != chapter_number:
        raise HTTPException(status_code=404, detail="Workflow introuvable.")
    return _workflow_run_payload(run)


@router.post("/{chapter_number}/review")
def review_chapter(book_id: str, chapter_number: int, payload: ReviewPayload = Body(default_factory=ReviewPayload), container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_book(book_id, container)
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


@router.post("/{chapter_number}/approve")
def approve_chapter(book_id: str, chapter_number: int, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_book(book_id, container)
    try:
        result = container.approve_chapter_and_sync_canon().execute(book, chapter_number=chapter_number)
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


@router.post("/{chapter_number}/reject")
def reject_chapter(book_id: str, chapter_number: int, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_book(book_id, container)
    try:
        updated_book = container.reject_chapter().execute(book, chapter_number=chapter_number)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return updated_book.model_dump(mode="json")


@router.get("/{chapter_number}/context")
def get_canonical_context(book_id: str, chapter_number: int, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_book(book_id, container)
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
