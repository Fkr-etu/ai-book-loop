from __future__ import annotations

from enum import StrEnum
from pydantic import BaseModel, Field


class ChapterStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    NEEDS_REVIEW = "needs_review"


class SceneReview(BaseModel):
    score: int = Field(ge=0, le=10)
    approved: bool
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


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
    outline: str | None = None
    outline_approved: bool = False
    chapters: list[Chapter] = Field(default_factory=list)
