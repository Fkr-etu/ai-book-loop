from __future__ import annotations

from enum import StrEnum
from pydantic import BaseModel, Field, model_validator


class ChapterStatus(StrEnum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANONICAL = "canonical"
    NEEDS_REVIEW = "needs_review"


class SceneReview(BaseModel):
    score: int = Field(ge=0, le=10)
    approved: bool
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class OutlineChapter(BaseModel):
    number: int = Field(gt=0)
    title: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    synopsis: str = ""


class Outline(BaseModel):
    chapters: list[OutlineChapter] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_chapter_numbers(self) -> "Outline":
        numbers = [chapter.number for chapter in self.chapters]
        if numbers != list(range(1, len(numbers) + 1)):
            raise ValueError("Outline chapter numbers must be consecutive starting at 1")
        return self

    def render(self) -> str:
        lines = []
        for chapter in self.chapters:
            lines.append(f"Chapter {chapter.number}: {chapter.title}")
            lines.append(f"Objective: {chapter.objective}")
            if chapter.synopsis:
                lines.append(f"Synopsis: {chapter.synopsis}")
        return "\n".join(lines)


class Chapter(BaseModel):
    id: str
    number: int = Field(gt=0)
    title: str
    objective: str
    status: ChapterStatus = ChapterStatus.DRAFT
    current_version: int = Field(default=0, ge=0)
    summary: str | None = None


class BookState(BaseModel):
    id: str
    title: str
    theme: str
    author_idea: str
    lore: str = ""
    constraints: list[str] = Field(default_factory=list)
    outline: Outline | None = None
    outline_approved: bool = False
    chapters: list[Chapter] = Field(default_factory=list)
