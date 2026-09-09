from __future__ import annotations

from book_loop.domain.protocols import EmbeddingProvider
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.embeddings.fake import FakeEmbeddingProvider
from book_loop.infrastructure.embeddings.gemini import GeminiEmbeddingProvider


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "fake" or not settings.gemini_api_key:
        return FakeEmbeddingProvider()
    if settings.embedding_provider == "gemini":
        return GeminiEmbeddingProvider(
            api_key=settings.gemini_api_key,
            model=settings.embedding_model,
        )
    return FakeEmbeddingProvider()
