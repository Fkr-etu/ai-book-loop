from __future__ import annotations

from book_loop.agents.outline import OutlineAgent
from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.application.use_cases.add_chapter import AddChapter
from book_loop.application.use_cases.approve_chapter import ApproveChapter
from book_loop.application.use_cases.approve_chapter_and_sync_canon import ApproveChapterAndSyncCanon
from book_loop.application.use_cases.approve_outline import ApproveOutline
from book_loop.application.use_cases.create_book import CreateBook
from book_loop.application.use_cases.extract_chapter_assertions import ExtractChapterAssertions
from book_loop.application.use_cases.generate_chapter import GenerateChapter
from book_loop.application.use_cases.generate_outline import GenerateOutline
from book_loop.application.use_cases.ingest_document import IngestDocument
from book_loop.application.use_cases.reject_chapter import RejectChapter
from book_loop.application.use_cases.review_assertion import ReviewAssertion
from book_loop.application.use_cases.review_chapter import ReviewChapter
from book_loop.application.use_cases.set_creative_brief import SetCreativeBrief
from book_loop.application.use_cases.update_book import UpdateBook
from book_loop.application.use_cases.update_outline import UpdateOutline
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.database.repository import SQLiteBookRepository
from book_loop.infrastructure.llm.assertion_extractor import LLMAssertionExtractor
from book_loop.infrastructure.llm.factory import create_llm
from book_loop.workflow.chapter_graph import ChapterWorkflow


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
        self.context_builder = ContextBuilder(knowledge_repository=self.repository)
        self.linter = ChapterLinter()

        self.chapter_workflow = ChapterWorkflow(
            repository=self.repository,
            writer=self.writer_agent,
            reviewer=self.reviewer_agent,
            summarizer=self.summarizer_agent,
            context_builder=self.context_builder,
            linter=self.linter,
            max_retries=self.settings.max_retries,
            review_threshold=self.settings.review_threshold,
        )

    def create_book(self) -> CreateBook:
        return CreateBook(self.repository)

    def set_creative_brief(self) -> SetCreativeBrief:
        return SetCreativeBrief(self.repository)

    def update_book(self) -> UpdateBook:
        return UpdateBook(self.repository)

    def generate_outline(self) -> GenerateOutline:
        return GenerateOutline(self.repository, self.outline_agent)

    def update_outline(self) -> UpdateOutline:
        return UpdateOutline(self.repository)

    def approve_outline(self) -> ApproveOutline:
        return ApproveOutline(self.repository)

    def add_chapter(self) -> AddChapter:
        return AddChapter(self.repository)

    def generate_chapter(self) -> GenerateChapter:
        return GenerateChapter(self.chapter_workflow)

    def review_chapter(self) -> ReviewChapter:
        return ReviewChapter(
            repository=self.repository,
            reviewer=self.reviewer_agent,
            context_builder=self.context_builder,
            linter=self.linter,
            max_retries=self.settings.max_retries,
            threshold=self.settings.review_threshold,
        )

    def approve_chapter(self) -> ApproveChapter:
        return ApproveChapter(self.repository)

    def approve_chapter_and_sync_canon(self) -> ApproveChapterAndSyncCanon:
        extractor = LLMAssertionExtractor(self.llm)
        return ApproveChapterAndSyncCanon(
            book_repository=self.repository,
            knowledge_repository=self.repository,
            extractor=extractor,
        )

    def reject_chapter(self) -> RejectChapter:
        return RejectChapter(self.repository)

    def ingest_document(self) -> IngestDocument:
        extractor = LLMAssertionExtractor(self.llm)
        return IngestDocument(repository=self.repository, extractor=extractor)

    def extract_chapter_assertions(self) -> ExtractChapterAssertions:
        extractor = LLMAssertionExtractor(self.llm)
        return ExtractChapterAssertions(
            book_repository=self.repository,
            knowledge_repository=self.repository,
            extractor=extractor,
        )

    def review_assertion(self) -> ReviewAssertion:
        return ReviewAssertion(self.repository)
