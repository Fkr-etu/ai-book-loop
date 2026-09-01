from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChapterSummary:
    """Canonical summary of an approved chapter."""

    chapter_number: int
    title: str
    summary: str

    def render(self) -> str:
        return f"Chapter {self.chapter_number} ({self.title}): {self.summary}"
