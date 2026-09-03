from book_loop.agents.writer import WriterAgent
from book_loop.application.services.context import ContextBuilder
from book_loop.application.use_cases.approve_chapter_and_sync_canon import ApproveChapterAndSyncCanon
from book_loop.application.use_cases.review_assertion import ReviewAssertion
from book_loop.domain.models import (
    BookState,
    Chapter,
    DocumentChunk,
    ExtractedAssertion,
    Outline,
    ReviewDecisionType,
)
from book_loop.infrastructure.database.repository import SQLiteBookRepository


class MarseilleAssertionExtractor:
    def extract(self, *, chunk: DocumentChunk) -> list[ExtractedAssertion]:
        marker = "Céleste conserve une cassette analogique au Vieux-Port."
        start = chunk.content.index(marker)
        return [
            ExtractedAssertion(
                statement="Céleste conserve une cassette analogique au Vieux-Port.",
                subject="Céleste",
                predicate="conserve une cassette analogique au Vieux-Port",
                object="oui",
                confidence=0.99,
                start_offset=start,
                end_offset=start + len(marker),
            )
        ]


class RecordingLLM:
    def __init__(self) -> None:
        self.last_user_prompt = ""

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.last_user_prompt = user_prompt
        return "Une nouvelle scène de Marseille respecte le Canon établi."


def test_les_veilleurs_canon_e2e_validation(tmp_path):
    repo = SQLiteBookRepository(f"sqlite:///{tmp_path / 'canon.db'}")
    book = BookState(
        id="les-veilleurs-de-marseille",
        title="Les Veilleurs de Marseille",
        theme="thriller futuriste",
        author_idea="Une archiviste découvre que certains souvenirs de Marseille ont été volontairement effacés.",
        outline=Outline(chapters=[{"number": 1, "title": "Les Archives Silence", "objective": "Découvrir la trace d'un souvenir effacé."}]),
        outline_approved=True,
        chapters=[Chapter(id="chapter-1", number=1, title="Les Archives Silence", objective="Découvrir la trace d'un souvenir effacé.")],
    )
    repo.save(book)
    chapter_text = (
        "À Marseille, Céleste parcourt les archives interdites. "
        "Céleste conserve une cassette analogique au Vieux-Port. "
        "Elle comprend que certains souvenirs ont été effacés."
    )
    repo.save_chapter_version(book.id, 1, 1, chapter_text)

    # 1. Extraction Canon from the approved chapter.
    book = repo.get(book.id)
    book.chapters[0].status = "approved"
    repo.save(book)
    sync = ApproveChapterAndSyncCanon(
        book_repository=repo,
        knowledge_repository=repo,
        extractor=MarseilleAssertionExtractor(),
    ).execute(book, chapter_number=1)
    assert sync.ingestion.assertions
    assert sync.ingestion.evidence

    # 2. Human validation of an assertion.
    assertion = sync.ingestion.assertions[0]
    decision = ReviewAssertion(repo).execute(
        book_id=book.id,
        assertion_id=assertion.id,
        decision=ReviewDecisionType.ACCEPT,
        reviewer_id="canon-e2e",
        rationale="Validated against the approved chapter evidence.",
    )
    assert decision.decision is ReviewDecisionType.ACCEPT

    # 3. Promotion: accepted assertion becomes an active CanonicalFact.
    facts = repo.list_active_canonical_facts(book_id=book.id)
    assert len(facts) == 1
    assert facts[0].assertion_id == assertion.id
    assert facts[0].statement == assertion.statement

    # 4. New generation must receive the active Canon in its prompt context.
    llm = RecordingLLM()
    context = ContextBuilder(knowledge_repository=repo).for_chapter(repo.get(book.id), 1)
    generated = WriterAgent(llm).write(context=context)
    assert generated
    assert "CANONICAL KNOWLEDGE:" in llm.last_user_prompt
    assert assertion.statement in llm.last_user_prompt
    assert f"fact_id={facts[0].id}" in llm.last_user_prompt
