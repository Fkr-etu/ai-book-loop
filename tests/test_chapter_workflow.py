from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import BookState, Chapter
from book_loop.workflow.chapter_graph import ChapterWorkflow
from book_loop.infrastructure.database.repository import SQLiteBookRepository
import tempfile


class FakeLLM:
    def __init__(self):
        self.calls = 0

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        if "Review" in system_prompt:
            return '{"score": 9, "approved": true, "issues": [], "suggestions": []}'
        if "canonical continuity" in system_prompt.lower():
            return "Canonical summary."
        return "A valid chapter draft."


def test_workflow_requires_approved_outline() -> None:
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        repo = SQLiteBookRepository(f"sqlite:///{tmp.name}")
        book = BookState(
            id="b",
            title="B",
            theme="T",
            author_idea="I",
            outline="Outline",
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
            outline="Outline",
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
