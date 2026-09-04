from book_loop.agents.reviewer import ReviewerAgent
from book_loop.agents.summarizer import SummarizerAgent
from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.services.linter import ChapterLinter
from book_loop.domain.models import (
    BookState,
    Chapter,
    ChapterStatus,
    Diagnostic,
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticSource,
    LinguisticCheckResult,
    LinguisticCheckStatus,
    Outline,
    SceneReview,
)
from book_loop.workflow.chapter_graph import ChapterWorkflow


class RecordingLLM:
    def __init__(self, drafts):
        self.drafts = iter(drafts)
        self.reviewer_prompts = []

    def generate(self, *, system_prompt, user_prompt):
        if "writer" in system_prompt.lower() or "editor" in system_prompt.lower():
            return next(self.drafts)
        if "summar" in system_prompt.lower():
            return "Summary."
        raise AssertionError(system_prompt)

    def generate_structured(self, *, system_prompt, user_prompt, schema, thinking_level="medium", max_output_tokens=None):
        self.reviewer_prompts.append(user_prompt)
        return schema(score=9, approved=True, issues=[], suggestions=[])


class Repository:
    def __init__(self, book):
        self.books = {book.id: book}
        self.versions = []
        self.reviews = []

    def save(self, book):
        self.books[book.id] = book

    def get(self, book_id):
        return self.books[book_id]

    def save_chapter_version(self, book_id, chapter_number, version, draft):
        self.versions.append((book_id, chapter_number, version, draft))

    def get_chapter_version(self, book_id, chapter_number, version):
        for stored in reversed(self.versions):
            if stored[:3] == (book_id, chapter_number, version):
                return stored[3]
        raise KeyError((book_id, chapter_number, version))

    def save_review(self, book_id, chapter_number, version, review):
        self.reviews.append((book_id, chapter_number, version, review))


class FakeValidation:
    def __init__(self, results):
        self.results = iter(results)

    def validate(self, text):
        return next(self.results)

    @staticmethod
    def blocking_diagnostics(result):
        return [d for d in result.diagnostics if d.severity == DiagnosticSeverity.ERROR]


class FakeCanon:
    def __init__(self, results):
        self.results = iter(results)

    def check(self, text, *, book_id):
        return next(self.results)


def make_book():
    return BookState(
        id="b1",
        title="Book",
        theme="Thriller",
        author_idea="Idea",
        outline=Outline(chapters=[{"number": 1, "title": "One", "objective": "Start"}]),
        outline_approved=True,
        chapters=[Chapter(id="c1", number=1, title="One", objective="Start")],
    )


def result(diagnostics):
    return LinguisticCheckResult(
        status=LinguisticCheckStatus.ISSUES_FOUND if diagnostics else LinguisticCheckStatus.NO_ISSUES_FOUND,
        diagnostics=diagnostics,
        checker="fake",
    )


def test_blocking_linguistic_diagnostic_triggers_bounded_retry_and_preserves_versions():
    book = make_book()
    repository = Repository(book)
    llm = RecordingLLM(["Draft with grammar error.", "Corrected draft."])
    blocking = Diagnostic(
        category=DiagnosticCategory.AGREEMENT,
        severity=DiagnosticSeverity.ERROR,
        source=DiagnosticSource.NLP,
        message="Subject-verb disagreement",
        start_offset=0,
        end_offset=10,
        original_text="Les veilleur",
        suggestions=["Les veilleurs"],
        confidence=0.95,
        rule_id="SPACY_FR_SUBJECT_VERB_NUMBER",
    )
    workflow = ChapterWorkflow(
        repository=repository,
        writer=WriterAgent(llm),
        reviewer=ReviewerAgent(llm),
        summarizer=SummarizerAgent(llm),
        context_builder=ContextBuilder(),
        linter=ChapterLinter(),
        validation_service=FakeValidation([result([blocking]), result([])]),
        canon_checker=FakeCanon([result([]), result([])]),
        max_retries=2,
    )

    state = workflow.run(book=book, chapter_number=1)

    assert state.attempt == 2
    assert state.decision == "accept"
    assert [item[2] for item in repository.versions] == [1, 2]
    assert repository.reviews[0][3].approved is False
    assert "Subject-verb disagreement" in repository.reviews[0][3].issues[0]
    assert len(llm.reviewer_prompts) == 1


def test_non_blocking_diagnostics_are_passed_to_reviewer_without_retry():
    book = make_book()
    repository = Repository(book)
    llm = RecordingLLM(["Clean literary draft."])
    warning = Diagnostic(
        category=DiagnosticCategory.SYNTAX,
        severity=DiagnosticSeverity.WARNING,
        source=DiagnosticSource.NLP,
        message="Possible sentence fragment",
        start_offset=0,
        end_offset=12,
        original_text="Le silence.",
        confidence=0.65,
        rule_id="SPACY_FR_NO_VERB",
    )
    workflow = ChapterWorkflow(
        repository=repository,
        writer=WriterAgent(llm),
        reviewer=ReviewerAgent(llm),
        summarizer=SummarizerAgent(llm),
        context_builder=ContextBuilder(),
        linter=ChapterLinter(),
        validation_service=FakeValidation([result([warning])]),
        canon_checker=FakeCanon([result([])]),
    )

    state = workflow.run(book=book, chapter_number=1)

    assert state.attempt == 1
    assert state.decision == "accept"
    assert len(repository.versions) == 1
    assert "DETERMINISTIC DIAGNOSTICS" in llm.reviewer_prompts[0]
    assert "Possible sentence fragment" in llm.reviewer_prompts[0]
    assert repository.books["b1"].chapters[0].status == ChapterStatus.APPROVED
