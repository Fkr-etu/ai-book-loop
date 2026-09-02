from __future__ import annotations

from typing import Protocol

from book_loop.domain.models import (
    Assertion,
    BookState,
    DocumentChunk,
    Evidence,
    SceneReview,
    SourceDocument,
)


class LLMProvider(Protocol):
    def generate(self, *, system_prompt: str, user_prompt: str) -> str: ...


class Writer(Protocol):
    def write(self, *, context: str) -> str: ...


class Reviewer(Protocol):
    def review(self, *, context: str, draft: str) -> SceneReview: ...


class Summarizer(Protocol):
    def summarize(self, *, context: str, chapter: str) -> str: ...


class BookRepository(Protocol):
    def save(self, book: BookState) -> None: ...
    def get(self, book_id: str) -> BookState: ...
    def save_chapter_version(
        self, book_id: str, chapter_number: int, version: int, draft: str
    ) -> None: ...
    def save_review(
        self, book_id: str, chapter_number: int, version: int, review: SceneReview
    ) -> None: ...


class AssertionExtractor(Protocol):
    def extract(self, *, chunk: DocumentChunk) -> list[object]: ...


class KnowledgeRepository(Protocol):
    def find_source_by_hash(self, *, book_id: str, content_hash: str) -> SourceDocument | None: ...
    def save_source(self, source: SourceDocument) -> None: ...
    def save_chunk(self, chunk: DocumentChunk) -> None: ...
    def save_assertion(self, assertion: Assertion) -> None: ...
    def save_evidence(self, evidence: Evidence) -> None: ...
