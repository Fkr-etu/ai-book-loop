from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from book_loop.api.dependencies import get_container, get_owned_book
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books/{book_id}/documents", tags=["documents"])


class IngestDocumentPayload(BaseModel):
    name: str
    sourceType: str = "markdown"
    content: str
    metadata: dict[str, str] | None = None


@router.post("/ingest")
def ingest_document(book_id: str, payload: IngestDocumentPayload, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
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
