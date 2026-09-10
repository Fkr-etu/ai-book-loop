from __future__ import annotations

from book_loop.agents.outline import OutlineAgent
from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.canon_validation import CanonDiagnosticChecker
from book_loop.application.services.canonical_fact_embedding_indexer import CanonicalFactEmbeddingIndexer
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.hybrid_retrieval import HybridCanonicalRetriever
from book_loop.application.services.linguistic_context import GeminiDiagnosticContextualizer
from book_loop.application.services.linguistic_validation import LinguisticValidationService
from book_loop.application.services.linter import ChapterLinter
from book_loop.application.services.retrieval import CanonicalRetriever
from book_loop.application.services.semantic_retrieval import EmbeddingCanonicalRetriever
from book_loop.application.use_cases.add_chapter import AddChapter
from book_loop.application.use_cases.analyze_canon_change import AnalyzeCanonChange
from book_loop.application.use_cases.analyze_consistency import AnalyzeConsistency
from book_loop.application.use_cases.approve_chapter import ApproveChapter
from book_loop.application.use_cases.approve_chapter_and_sync_canon import ApproveChapterAndSyncCanon
from book_loop.application.use_cases.approve_outline import ApproveOutline
from book_loop.application.use_cases.authenticate_user import AuthenticateUser
from book_loop.application.use_cases.create_book import CreateBook
from book_loop.application.use_cases.create_character import CreateCharacter
from book_loop.application.use_cases.create_character_relation import CreateCharacterRelation
from book_loop.application.use_cases.delete_character import DeleteCharacter
from book_loop.application.use_cases.delete_character_relation import DeleteCharacterRelation
from book_loop.application.use_cases.extract_chapter_assertions import ExtractChapterAssertions
from book_loop.application.use_cases.generate_chapter import GenerateChapter
from book_loop.application.use_cases.generate_outline import GenerateOutline
from book_loop.application.use_cases.get_analysis_job import GetAnalysisJob
from book_loop.application.use_cases.get_canonical_fact_history import GetCanonicalFactHistory
from book_loop.application.use_cases.get_character import GetCharacter
from book_loop.application.use_cases.ingest_document import IngestDocument
from book_loop.application.use_cases.list_canonical_facts import ListCanonicalFacts
from book_loop.application.use_cases.list_character_relations import ListCharacterRelations
from book_loop.application.use_cases.list_characters import ListCharacters
from book_loop.application.use_cases.login_user import LoginUser
from book_loop.application.use_cases.propose_canon_change import ProposeCanonChange
from book_loop.application.use_cases.reject_chapter import RejectChapter
from book_loop.application.use_cases.register_user import RegisterUser
from book_loop.application.use_cases.review_assertion import ReviewAssertion
from book_loop.application.use_cases.review_canon_change import ReviewCanonChange
from book_loop.application.use_cases.review_chapter import ReviewChapter
from book_loop.application.use_cases.set_creative_brief import SetCreativeBrief
from book_loop.application.use_cases.start_consistency_analysis import StartConsistencyAnalysis
from book_loop.application.use_cases.update_book import UpdateBook
from book_loop.application.use_cases.update_character import UpdateCharacter
from book_loop.application.use_cases.update_outline import UpdateOutline
from book_loop.infrastructure.auth import Argon2PasswordHasher, DUMMY_PASSWORD_HASH, JwtTokenService
from book_loop.infrastructure.auth_rate_limit import AuthRateLimiter
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.database.analysis_jobs import PostgresAnalysisJobStore
from book_loop.infrastructure.database.canon_change_postgres import PostgresCanonChangeRepository
from book_loop.infrastructure.database.postgres import PostgresWorkflowRunStore
from book_loop.infrastructure.database.temporal_context import TemporalContextStore
from book_loop.infrastructure.embeddings.factory import create_embedding_provider
from book_loop.infrastructure.llm.assertion_extractor import LLMAssertionExtractor
from book_loop.infrastructure.llm.factory import create_llm
from book_loop.infrastructure.linguistic.languagetool import LanguageToolChecker
from book_loop.infrastructure.linguistic.spacy import SpacyFrenchChecker
from book_loop.infrastructure.observability import ObservabilityStore
from book_loop.infrastructure.stripe_billing import StripeBillingRepository, StripeBillingService
from book_loop.infrastructure.workflow.chapter_workflow_adapter import ChapterWorkflowAdapter
from book_loop.workflow.chapter_graph import ChapterWorkflow


class Container:
    """Composition root: infrastructure wiring lives here, not in the domain."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        if not self.settings.database_url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
            raise ValueError("Unsupported DATABASE_URL; PostgreSQL is required (postgresql://...)")
        self.repository = PostgresCanonChangeRepository(self.settings.database_url)
        self.temporal_context_store = TemporalContextStore(self.repository)
        self.billing_repository = StripeBillingRepository(self.settings.database_url)
        self.billing = StripeBillingService(self.settings, self.billing_repository)
        self.auth_rate_limiter = AuthRateLimiter(self.settings.database_url)
        self.password_hasher = Argon2PasswordHasher()
        self.token_service = JwtTokenService(self.settings.auth_secret_key)
        self.workflow_store = PostgresWorkflowRunStore(self.settings.database_url)
        self.analysis_job_store = PostgresAnalysisJobStore(self.settings.database_url)
        self.observability = ObservabilityStore(self.settings.database_url)
        self.llm = create_llm(self.settings)
        self.embedding_provider = create_embedding_provider(self.settings)
        self.embedding_indexer = CanonicalFactEmbeddingIndexer(provider=self.embedding_provider, repository=self.repository, model=self.settings.embedding_model)
        self.semantic_retriever = EmbeddingCanonicalRetriever(self.embedding_provider, embedding_store=self.repository, embedding_model=self.settings.embedding_model)
        self.canonical_retriever = HybridCanonicalRetriever(CanonicalRetriever(), self.semantic_retriever)
        self.outline_agent = OutlineAgent(self.llm)
        self.writer_agent = WriterAgent(self.llm)
        self.reviewer_agent = ReviewerAgent(self.llm)
        self.summarizer_agent = SummarizerAgent(self.llm)
        self.context_builder = ContextBuilder(knowledge_repository=self.repository, retriever=self.canonical_retriever)
        self.linter = ChapterLinter()
        self.linguistic_contextualizer = GeminiDiagnosticContextualizer(llm=self.llm)
        self.chapter_workflow = ChapterWorkflow(repository=self.repository, writer=self.writer_agent, reviewer=self.reviewer_agent, summarizer=self.summarizer_agent, context_builder=self.context_builder, linter=self.linter, linguistic_validator_factory=self._linguistic_validator, linguistic_contextualizer=self._contextualize_linguistic_diagnostics, linguistic_language=self.settings.linguistic_language, max_retries=self.settings.max_retries, review_threshold=self.settings.review_threshold, workflow_store=self.workflow_store, observability=self.observability)
        self.chapter_workflow_port = ChapterWorkflowAdapter(self.chapter_workflow, self.workflow_store)
        self.register_user_use_case = RegisterUser(self.repository, self.password_hasher, self.token_service, self.auth_rate_limiter, rate_limit=self.settings.auth_register_rate_limit, rate_window_seconds=self.settings.auth_register_rate_window_seconds)
        self.login_user_use_case = LoginUser(self.repository, self.password_hasher, self.token_service, self.auth_rate_limiter, email_limit=self.settings.auth_login_rate_limit, email_window_seconds=self.settings.auth_login_rate_window_seconds, ip_limit=self.settings.auth_login_ip_rate_limit, ip_window_seconds=self.settings.auth_login_ip_rate_window_seconds, dummy_password_hash=DUMMY_PASSWORD_HASH)
        self.authenticate_user_use_case = AuthenticateUser(self.repository, self.token_service)

    def _contextualize_linguistic_diagnostics(self, chapter: str, diagnostics):
        return self.linguistic_contextualizer.review(chapter=chapter, diagnostics=diagnostics)

    def _linguistic_validator(self, book):
        mode = self.settings.linguistic_checker.strip().lower()
        if mode in {"", "disabled", "off", "none"}:
            return LinguisticValidationService(())
        checkers = []
        if mode in {"languagetool", "both", "all"}:
            checkers.append(LanguageToolChecker(base_url=self.settings.language_tool_url))
        if mode in {"spacy", "both", "all"}:
            checkers.append(SpacyFrenchChecker(model_name=self.settings.spacy_model))
        if mode in {"canon", "all", "both", "languagetool", "spacy"}:
            checkers.append(CanonDiagnosticChecker(book_id=book.id, knowledge_repository=self.repository, assertion_extractor=LLMAssertionExtractor(self.llm)))
        if not checkers:
            raise ValueError("Unsupported LINGUISTIC_CHECKER value; use disabled, languagetool, spacy, canon, both or all")
        return LinguisticValidationService(checkers)

    def create_book(self) -> CreateBook: return CreateBook(self.repository)
    def set_creative_brief(self) -> SetCreativeBrief: return SetCreativeBrief(self.repository)
    def update_book(self) -> UpdateBook: return UpdateBook(self.repository)
    def create_character(self) -> CreateCharacter: return CreateCharacter(self.repository)
    def get_character(self) -> GetCharacter: return GetCharacter(self.repository)
    def list_characters(self) -> ListCharacters: return ListCharacters(self.repository)
    def update_character(self) -> UpdateCharacter: return UpdateCharacter(self.repository)
    def delete_character(self) -> DeleteCharacter: return DeleteCharacter(self.repository)
    def create_character_relation(self) -> CreateCharacterRelation: return CreateCharacterRelation(self.repository)
    def list_character_relations(self) -> ListCharacterRelations: return ListCharacterRelations(self.repository)
    def delete_character_relation(self) -> DeleteCharacterRelation: return DeleteCharacterRelation(self.repository)
    def generate_outline(self) -> GenerateOutline: return GenerateOutline(self.repository, self.outline_agent)
    def update_outline(self) -> UpdateOutline: return UpdateOutline(self.repository)
    def approve_outline(self) -> ApproveOutline: return ApproveOutline(self.repository)
    def add_chapter(self) -> AddChapter: return AddChapter(self.repository)
    def generate_chapter(self) -> GenerateChapter: return GenerateChapter(self.chapter_workflow_port, repository=self.repository, workflow_store=self.workflow_store, book_usage=self.repository)
    def review_chapter(self) -> ReviewChapter: return ReviewChapter(repository=self.repository, reviewer=self.reviewer_agent, context_builder=self.context_builder, linter=self.linter, max_retries=self.settings.max_retries, threshold=self.settings.review_threshold)
    def approve_chapter(self) -> ApproveChapter: return ApproveChapter(self.repository)
    def approve_chapter_and_sync_canon(self) -> ApproveChapterAndSyncCanon: return ApproveChapterAndSyncCanon(book_repository=self.repository, knowledge_repository=self.repository, extractor=LLMAssertionExtractor(self.llm), temporal_context_store=self.temporal_context_store)
    def reject_chapter(self) -> RejectChapter: return RejectChapter(self.repository)
    def ingest_document(self) -> IngestDocument: return IngestDocument(repository=self.repository, extractor=LLMAssertionExtractor(self.llm), temporal_context_store=self.temporal_context_store)
    def extract_chapter_assertions(self) -> ExtractChapterAssertions: return ExtractChapterAssertions(book_repository=self.repository, knowledge_repository=self.repository, extractor=LLMAssertionExtractor(self.llm), temporal_context_store=self.temporal_context_store)
    def review_assertion(self) -> ReviewAssertion: return ReviewAssertion(self.repository, embedding_indexer=self.embedding_indexer)
    def propose_canon_change(self) -> ProposeCanonChange: return ProposeCanonChange(self.repository)
    def review_canon_change(self) -> ReviewCanonChange: return ReviewCanonChange(self.repository, embedding_indexer=self.embedding_indexer)
    def list_canonical_facts(self) -> ListCanonicalFacts: return ListCanonicalFacts(self.repository)
    def get_canonical_fact_history(self) -> GetCanonicalFactHistory: return GetCanonicalFactHistory(self.repository)
    def analyze_consistency(self) -> AnalyzeConsistency: return AnalyzeConsistency(self.repository, temporal_context_store=self.temporal_context_store)
    def start_consistency_analysis(self) -> StartConsistencyAnalysis: return StartConsistencyAnalysis(self.repository, self.analysis_job_store)
    def get_analysis_job(self) -> GetAnalysisJob: return GetAnalysisJob(self.repository, self.analysis_job_store)
    def analyze_canon_change(self) -> AnalyzeCanonChange: return AnalyzeCanonChange(self.repository)
