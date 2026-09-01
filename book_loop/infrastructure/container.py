from __future__ import annotations

from book_loop.agents.outline import OutlineAgent
from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.application.use_cases.add_chapter import AddChapter
from book_loop.application.use_cases.approve_outline import ApproveOutline
from book_loop.application.use_cases.create_book import CreateBook
from book_loop.application.use_cases.generate_chapter import GenerateChapter
from book_loop.application.use_cases.generate_outline import GenerateOutline
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.database.repository import SQLiteBookRepository
from book_loop.infrastructure.llm.factory import create_llm
from book_loop.workflow.chapter import ChapterWorkflow


class Container:
    """Composition root: infrastructure wiring lives here, not in the domain."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.repository = SQLiteBookRepository(self.settings.database_url)
        self.llm = create_llm(self.settings)

        self.outline_agent = OutlineAgent(self.llm)
        self.writer_agent = WriterAgent(self.llm)
        self.reviewer_agent = ReviewerAgent(self.llm)
        self.summarizer_agent = SummarizerAgent(self.llm)

        self.chapter_workflow = ChapterWorkflow(
            repository=self.repository,
            writer=self.writer_agent,
            reviewer=self.reviewer_agent,
            summarizer=self.summarizer_agent,
            context_builder=ContextBuilder(),
            linter=ChapterLinter(),
            max_retries=self.settings.max_retries,
            review_threshold=self.settings.review_threshold,
        )

    def create_book(self) -> CreateBook:
        return CreateBook(self.repository)

    def generate_outline(self) -> GenerateOutline:
        return GenerateOutline(self.repository, self.outline_agent)

    def approve_outline(self) -> ApproveOutline:
        return ApproveOutline(self.repository)

    def add_chapter(self) -> AddChapter:
        return AddChapter(self.repository)

    def generate_chapter(self) -> GenerateChapter:
        return GenerateChapter(self.chapter_workflow)
