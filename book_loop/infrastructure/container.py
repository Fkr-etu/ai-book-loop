from __future__ import annotations

from book_loop.agents.outline import OutlineAgent
from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.application.services.linguistic_context import GeminiDiagnosticContextualizer
from book_loop.application.services.linguistic_validation import LinguisticValidationService
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
from book_loop.infrastructure.linguistic.languagetool import LanguageToolChecker
from book_loop.infrastructure.linguistic.spacy import SpacyFrenchChecker
from book_loop.infrastructure.llm.assertion_extractor import LLMAssertionExtractor
from book_loop.infrastructure.llm.factory import create_llm
from book_loop.application.services.canon_validation import CanonDiagnosticChecker
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
        self.assertion_extractor = LLMAssertionExtractor(self.llm)
        self.diagnostic_contextualizer = GeminiDiagnosticContextualizer(llm=self.llm)
        self.linguistic_validation = LinguisticValidationService(
            self._build_linguistic_checkers(),
            contextualizer=self.diagnostic_contextualizer,
        )
        self.canon_checker = CanonDiagnosticChecker(
            knowledge_repository=self.repository,
            assertion_extractor=self.assertion_extractor,
        )

        self.chapter_workflow = ChapterWorkflow(
            repository=self.repository,
            writer=self.writer_agent,
            reviewer=self.reviewer_agent,
            summarizer=self.summarizer_agent,
            context_builder=self.context_builder,
            linter=self.linter,
            validation_service=self.linguistic_validation,
            canon_checker=self.canon_checker,
            max_retries=self.settings.max_retries,
            review_threshold=self.settings.review_threshold,
        )

    def _build_linguistic_checkers(self):
        if self.settings.linguistic_checker == "disabled":
            return []
        if self.settings.linguistic_checker == "spacy":
            return [SpacyFrenchChecker(model_name=self.settings.spacy_model)]
        if self.settings.linguistic_checker == "language_tool":
            return [LanguageToolChecker(base_url=self.settings.language_tool_url)]
        if self.settings.linguistic_checker == "hybrid":
            return [
                LanguageToolChecker(base_url=self.settings.language_tool_url),
                SpacyFrenchChecker(model_name=self.settings.spacy_model),
            ]
        raise ValueError(
            "LINGUISTIC_CHECKER must be one of: disabled, spacy, language_tool, hybrid"
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
        return ApproveChapterAndSyncCanon(
            book_repository=self.repository,
            knowledge_repository=self.repository,
            extractor=self.assertion_extractor,
        )

    def reject_chapter(self) -> RejectChapter:
        return RejectChapter(self.repository)

    def ingest_document(self) -> IngestDocument:
        return IngestDocument(repository=self.repository, extractor=self.assertion_extractor)

    def extract_chapter_assertions(self) -> ExtractChapterAssertions:
        return ExtractChapterAssertions(
            book_repository=self.repository,
            knowledge_repository=self.repository,
            extractor=self.assertion_extractor,
        )

    def review_assertion(self) -> ReviewAssertion:
        return ReviewAssertion(self.repository)
