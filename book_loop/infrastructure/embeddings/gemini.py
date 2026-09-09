from __future__ import annotations

from collections.abc import Sequence

from google import genai
from google.genai import types

from book_loop.domain.protocols import EmbeddingProvider


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Gemini embedding adapter kept behind the application-facing protocol."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gemini-embedding-001",
    ) -> None:
        if not api_key.strip():
            raise ValueError("A Gemini API key is required for live embeddings")
        if not model.strip():
            raise ValueError("A Gemini embedding model is required")
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def embed(self, *, text: str) -> Sequence[float]:
        if not text.strip():
            raise ValueError("Embedding text must not be empty")
        result = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
        )
        if not result.embeddings:
            raise RuntimeError("Gemini returned no embedding")
        values = result.embeddings[0].values
        if not values:
            raise RuntimeError("Gemini returned an empty embedding")
        return tuple(values)
