from __future__ import annotations

from types import SimpleNamespace

from book_loop.application.use_cases.start_document_ingestion import StartDocumentIngestion


class FakeJobStore:
    def __init__(self) -> None:
        self.calls = []

    def enqueue(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(**kwargs, model_dump=lambda mode=None: {})


class FakeIngest:
    def __init__(self) -> None:
        self.calls = []

    def prepare(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(content_hash="abc123"), [], False


class FakeRepository:
    def get(self, book_id: str):
        return SimpleNamespace(id=book_id, owner_id="owner-1")


def test_start_document_ingestion_prepares_source_and_enqueues_content_hash():
    job_store = FakeJobStore()
    ingest = FakeIngest()
    use_case = StartDocumentIngestion(FakeRepository(), job_store, ingest)

    use_case.execute(
        book_id="book-1",
        owner_id="owner-1",
        name="manuscrit.md",
        source_type="markdown",
        content="Alice vit ici.",
    )

    assert ingest.calls[0]["book_id"] == "book-1"
    assert job_store.calls == [{
        "book_id": "book-1",
        "owner_id": "owner-1",
        "analysis_type": "ingestion",
        "idempotency_key": "abc123",
    }]
