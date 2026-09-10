from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from book_loop.api.dependencies import get_container, get_owned_book
from book_loop.application.use_cases.start_document_ingestion import StartDocumentIngestion
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books/{book_id}/documents", tags=["documents"])


class IngestDocumentPayload(BaseModel):
    name: str
    sourceType: str = "markdown"
    content: str
    metadata: dict[str, str] | None = None


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_document(book_id: str, payload: IngestDocumentPayload, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    try:
        job = StartDocumentIngestion(
            repository=container.repository,
            job_store=container.analysis_job_store,
            ingest_document=container.ingest_document(),
        ).execute(
            book_id=book.id,
            owner_id=book.owner_id,
            name=payload.name,
            source_type=payload.sourceType,
            content=payload.content,
            metadata=payload.metadata,
        )
        return job.model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/ingest/{job_id}")
def get_ingestion_job(book_id: str, job_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    try:
        job = container.get_analysis_job().execute(job_id=job_id, owner_id=book.owner_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Import introuvable") from exc
    if job.book_id != book_id or job.analysis_type != "ingestion":
        raise HTTPException(status_code=404, detail="Import introuvable")
    return job.model_dump(mode="json")
