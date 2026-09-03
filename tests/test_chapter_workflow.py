from __future__ import annotations

import tempfile

from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import BookState, Chapter, Outline, SceneReview
from book_loop.infrastructure.database.repository import SQLiteBookRepository
from book_loop.workflow.chapter_graph import ChapterWorkflow


class FakeLLM:
    def __init__(self):
        self.calls = 0

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        if "canonical continuity" in system_prompt.lower():
            return "Canonical summary."
        return "A valid chapter draft."

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[SceneReview],
        thinking_level: str = "medium",
        max_output_tokens: int | None = None,
    ) -> SceneReview:
        del system_prompt, user_prompt, thinking_level, max_output_tokens
        self.calls += 1
        return schema(score=9, approved=True, issues=[], suggestions=[])


def make_outline() -> Outline:
    return Outline(
        chapters=[
            {"number": 1, "title": "One", "objective": "Start"},
        ]
    )


def test_workflow_requires_approved_outline() -> None:
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        repo = SQLiteBookRepository(f"sqlite:///{tmp.name}")
        book = BookState(
            id="b",
            title="B",
            theme="T",
            author_idea="I",
            outline=make_outline(),
            outline_approved=False,
            chapters=[Chapter(id="c", number=1, title="One", objective="Start")],
        )
        repo.save(book)
        llm = FakeLLM()
        workflow = ChapterWorkflow(
            repository=repo,
            writer=WriterAgent(llm),
            reviewer=ReviewerAgent(llm),
            summarizer=SummarizerAgent(llm),
            context_builder=ContextBuilder(),
            linter=ChapterLinter(),
            max_retries=3,
            review_threshold=7,
        )
        try:
            workflow.run(book=book, chapter_number=1)
            assert False, "expected approval gate"
        except ValueError as exc:
            assert "approve" in str(exc).lower()


def test_workflow_generates_reviews_and_summary() -> None:
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        repo = SQLiteBookRepository(f"sqlite:///{tmp.name}")
        book = BookState(
            id="b",
            title="B",
            theme="T",
            author_idea="I",
            outline=make_outline(),
            outline_approved=True,
            chapters=[Chapter(id="c", number=1, title="One", objective="Start")],
        )
        repo.save(book)
        llm = FakeLLM()
        workflow = ChapterWorkflow(
            repository=repo,
            writer=WriterAgent(llm),
            reviewer=ReviewerAgent(llm),
            summarizer=SummarizerAgent(llm),
            context_builder=ContextBuilder(),
            linter=ChapterLinter(),
            max_retries=3,
            review_threshold=7,
        )
        state = workflow.run(book=book, chapter_number=1)
        assert state.decision == "accept"
        assert state.summary == "Canonical summary."
        assert state.attempt == 1
