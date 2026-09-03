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
    score: float = Field(ge=0, le=10)
    approved: bool
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class CreativeBrief(BaseModel):
    premise: str = Field(min_length=1)
    audience: str = ""
    tone: str = ""
    themes: list[str] = Field(default_factory=list)
    must_include: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)


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
    owner_id: str = ""
    title: str
    theme: str
    author_idea: str
    creative_brief: CreativeBrief | None = None
    lore: str = ""
    constraints: list[str] = Field(default_factory=list)
    outline: Outline | None = None
    outline_approved: bool = False
    chapters: list[Chapter] = Field(default_factory=list)


class User(BaseModel):
    id: str
    email: str
    password_hash: str
    name: str = ""
    created_at: str | None = None


class UserPublic(BaseModel):
    id: str
    email: str
    name: str = ""


class SourceDocument(BaseModel):
    id: str
    book_id: str
    name: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    content: str
    content_hash: str = Field(min_length=64, max_length=64)
    metadata: dict[str, str] = Field(default_factory=dict)
    version: int = Field(default=1, ge=1)


class DocumentChunk(BaseModel):
    id: str
    source_document_id: str
    content: str = Field(min_length=1)
    sequence: int = Field(ge=0)
    start_offset: int = Field(ge=0)
    end_offset: int = Field(gt=0)
    metadata: dict[str, str] = Field(default_factory=dict)


class AssertionStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class Evidence(BaseModel):
    id: str
    assertion_id: str
    source_document_id: str
    chunk_id: str
    start_offset: int = Field(ge=0)
    end_offset: int = Field(gt=0)
    excerpt: str = Field(min_length=1)


class Assertion(BaseModel):
    id: str
    source_document_id: str
    chunk_id: str
    statement: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    status: AssertionStatus = AssertionStatus.PROPOSED
    evidence_id: str


class ExtractedAssertion(BaseModel):
    statement: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    start_offset: int = Field(ge=0)
    end_offset: int = Field(gt=0)


class ConflictStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"


class Conflict(BaseModel):
    id: str
    book_id: str
    left_assertion_id: str
    right_assertion_id: str
    status: ConflictStatus = ConflictStatus.OPEN
    resolution_assertion_id: str | None = None


class ReviewDecisionType(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"
    DEFER = "defer"


class ReviewDecision(BaseModel):
    id: str
    assertion_id: str
    decision: ReviewDecisionType
    reviewer_id: str | None = None
    rationale: str = ""
    created_at: str | None = None


class CanonicalFact(BaseModel):
    id: str
    book_id: str
    assertion_id: str
    statement: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object: str = Field(min_length=1)
    decision_id: str
    version: int = Field(default=1, ge=1)
    active: bool = True


class IngestionResult(BaseModel):
    source_document: SourceDocument
    chunks: list[DocumentChunk] = Field(default_factory=list)
    assertions: list[Assertion] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    already_ingested: bool = False
