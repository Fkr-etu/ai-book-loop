from __future__ import annotations

import hashlib
import math

from book_loop.domain.protocols import EmbeddingProvider


class FakeEmbeddingProvider(EmbeddingProvider):
    """Deterministic local provider for tests and dependency-free environments."""

    def __init__(self, *, dimensions: int = 32) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    def embed(self, *, text: str) -> tuple[float, ...]:
        if not text.strip():
            raise ValueError("Embedding text must not be empty")
        values: list[float] = []
        for index in range(self.dimensions):
            digest = hashlib.sha256(f"{index}:{text}".encode("utf-8")).digest()
            raw = int.from_bytes(digest[:8], "big") / (2**64 - 1)
            values.append(raw * 2.0 - 1.0)
        norm = math.sqrt(sum(value * value for value in values))
        return tuple(value / norm for value in values)
