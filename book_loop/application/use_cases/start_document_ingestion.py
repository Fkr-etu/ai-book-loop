from __future__ import annotations

from book_loop.application.ports.analysis_jobs import AnalysisJobStore
from book_loop.domain.analysis_job import AnalysisJob


class StartDocumentIngestion:
    """Persist an import and enqueue its LLM processing on the durable worker queue."""

    def __init__(self, repository, job_store: AnalysisJobStore, ingest_document) -> None:
        self.repository = repository
        self.job_store = job_store
        self.ingest_document = ingest_document

    def execute(
        self,
        *,
        book_id: str,
        owner_id: str,
        name: str,
        source_type: str,
        content: str,
        metadata: dict[str, str] | None = None,
    ) -> AnalysisJob:
        book = self.repository.get(book_id)
        if book.owner_id != owner_id:
            raise KeyError(book_id)
        source, _, _ = self.ingest_document.prepare(
            book_id=book_id,
            name=name,
            source_type=source_type,
            content=content,
            metadata=metadata,
        )
        return self.job_store.enqueue(
            book_id=book_id,
            owner_id=owner_id,
            analysis_type="ingestion",
            idempotency_key=source.content_hash,
        )
