from __future__ import annotations
import traceback
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from book_loop.api.dependencies import get_book, get_container, get_owned_book
from book_loop.domain.models import ChapterStatus
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books/{book_id}/chapters", tags=["chapters"])
class AddChapterPayload(BaseModel): chapter_number: int = Field(gt=0)
class ReviewPayload(BaseModel): versionNumber: int | None = None; draftText: str | None = None
class ApprovePayload(BaseModel): versionNumber: int | None = None
class SaveDraftPayload(BaseModel): draft: str

def _run_chapter_workflow(container: Container, book_id: str, chapter_number: int, idempotency_key: str) -> None:
    print(f"[chapter-workflow] start book={book_id} chapter={chapter_number} key={idempotency_key}", flush=True)
    try:
        book = get_book(book_id, container); result = container.generate_chapter().execute(book, chapter_number=chapter_number, idempotency_key=idempotency_key); print(f"[chapter-workflow] finished book={book_id} chapter={chapter_number} result={result!r}", flush=True)
    except Exception as exc:
        print(f"[chapter-workflow] FAILED book={book_id} chapter={chapter_number} key={idempotency_key} error={type(exc).__name__}: {exc}", flush=True); traceback.print_exc(); raise

@router.post("")
def add_chapter(book_id: str, payload: AddChapterPayload, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    try: updated_book = container.add_chapter().execute(book, chapter_number=payload.chapter_number)
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    return updated_book.model_dump(mode="json")

@router.post("/{chapter_number}/versions")
def save_chapter_draft(book_id: str, chapter_number: int, payload: SaveDraftPayload, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    chapter = next((item for item in book.chapters if item.number == chapter_number), None)
    if chapter is None: raise HTTPException(status_code=404, detail=f"Chapitre {chapter_number} introuvable.")
    versions = container.repository.list_chapter_versions(book.id, chapter_number)
    next_version = max((int(item["version"]) for item in versions), default=0) + 1
    container.repository.save_chapter_version(book.id, chapter_number, next_version, payload.draft)
    chapter.current_version = next_version
    chapter.reviewed_version = None
    chapter.status = ChapterStatus.DRAFT
    container.repository.save(book)
    return book.model_dump(mode="json")

@router.post("/{chapter_number}/generate", status_code=202)
def generate_chapter(book_id: str, chapter_number: int, background_tasks: BackgroundTasks, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    try: run = container.generate_chapter().start(book, chapter_number=chapter_number)
    except PermissionError as exc: raise HTTPException(status_code=429, detail=str(exc)) from exc
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    background_tasks.add_task(_run_chapter_workflow, container, book_id, chapter_number, run.idempotency_key)
    return {"run": run.model_dump(mode="json")}

@router.get("/{chapter_number}/workflow-runs/latest")
def get_latest_workflow_run(book_id: str, chapter_number: int, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container); run = container.generate_chapter().latest(book_id, chapter_number); return {"run": run.model_dump(mode="json") if run is not None else None}

@router.get("/{chapter_number}/workflow-runs/{run_id}")
def get_workflow_run(book_id: str, chapter_number: int, run_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
    try: run = container.generate_chapter().get_run(run_id)
    except KeyError as exc: raise HTTPException(status_code=404, detail="Workflow run introuvable.") from exc
    if run.book_id != book_id or run.chapter_number != chapter_number: raise HTTPException(status_code=404, detail="Workflow run introuvable.")
    return {"run": run.model_dump(mode="json")}

@router.post("/{chapter_number}/review")
def review_chapter(book_id: str, chapter_number: int, request: Request, payload: ReviewPayload = Body(default_factory=ReviewPayload), container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    try: updated_book, review = container.review_chapter().execute(book, chapter_number=chapter_number, version_number=payload.versionNumber, draft_text=payload.draftText)
    except ValueError as exc: raise HTTPException(status_code=404 if "not found" in str(exc).lower() else 400, detail=str(exc)) from exc
    return {"book": updated_book.model_dump(mode="json"), "review": review.model_dump(mode="json")}

@router.post("/{chapter_number}/approve")
def approve_chapter(book_id: str, chapter_number: int, request: Request, payload: ApprovePayload = Body(default_factory=ApprovePayload), container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    try: result = container.approve_chapter_and_sync_canon().execute(book, chapter_number=chapter_number, version_number=payload.versionNumber)
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    except KeyError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
    response = result.book.model_dump(mode="json"); response["canonSync"] = {"sourceDocument": result.ingestion.source_document.model_dump(mode="json"), "assertionCount": len(result.ingestion.assertions), "evidenceCount": len(result.ingestion.evidence), "conflicts": [conflict.model_dump(mode="json") for conflict in result.conflicts]}; return response

@router.post("/{chapter_number}/reject")
def reject_chapter(book_id: str, chapter_number: int, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    try: updated_book = container.reject_chapter().execute(book, chapter_number=chapter_number)
    except ValueError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
    return updated_book.model_dump(mode="json")

@router.get("/{chapter_number}/context")
def get_canonical_context(book_id: str, chapter_number: int, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container); chapter = next((c for c in book.chapters if c.number == chapter_number), None)
    if chapter is None: raise HTTPException(status_code=404, detail=f"Chapitre {chapter_number} introuvable.")
    formatted = container.context_builder.for_chapter(book, chapter_number); prev_summaries = "\n".join(f"Chapter {c.number} ({c.title}): {c.summary}" for c in book.chapters if c.number < chapter_number and c.summary)
    return {"authorIdea": book.author_idea, "theme": book.theme, "lore": book.lore, "globalOutline": book.outline.model_dump(mode="json") if book.outline else None, "constraints": book.constraints, "previousSummaries": prev_summaries, "currentObjective": chapter.objective, "formattedContext": formatted}
