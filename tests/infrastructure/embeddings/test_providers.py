from __future__ import annotations

import pytest

from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.embeddings.fake import FakeEmbeddingProvider
from book_loop.infrastructure.embeddings.factory import create_embedding_provider
from book_loop.infrastructure.embeddings.gemini import GeminiEmbeddingProvider


def test_fake_embedding_is_deterministic_and_normalized() -> None:
    provider = FakeEmbeddingProvider(dimensions=8)

    first = provider.embed(text="Alice returns home")
    second = provider.embed(text="Alice returns home")

    assert first == second
    assert len(first) == 8
    assert sum(value * value for value in first) == pytest.approx(1.0)


def test_fake_embedding_rejects_blank_text() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        FakeEmbeddingProvider().embed(text="  ")


def test_gemini_embedding_requires_api_key() -> None:
    with pytest.raises(ValueError, match="API key"):
        GeminiEmbeddingProvider(api_key="")


def test_embedding_factory_uses_fake_without_api_key() -> None:
    provider = create_embedding_provider(Settings(gemini_api_key=""))

    assert isinstance(provider, FakeEmbeddingProvider)


def test_embedding_factory_selects_gemini_when_configured() -> None:
    provider = create_embedding_provider(
        Settings(
            gemini_api_key="test-key",
            embedding_provider="gemini",
            embedding_model="gemini-embedding-001",
        )
    )

    assert isinstance(provider, GeminiEmbeddingProvider)
    assert provider.model == "gemini-embedding-001"
