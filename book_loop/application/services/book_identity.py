from __future__ import annotations

import hashlib
import json
from typing import Any


def book_identity(*, title: str, theme: str, author_idea: str, lore: str = "", constraints: list[str] | None = None) -> str:
    """Return a deterministic identity for a book's initial creative brief.

    This is deliberately based on the creation inputs, not the mutable book id.
    It is an anti-abuse signal, not a cryptographic proof of authorship.
    """
    payload: dict[str, Any] = {
        "title": " ".join(title.split()).casefold(),
        "theme": " ".join(theme.split()).casefold(),
        "author_idea": " ".join(author_idea.split()).casefold(),
        "lore": " ".join(lore.split()).casefold(),
        "constraints": [" ".join(item.split()).casefold() for item in (constraints or [])],
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
