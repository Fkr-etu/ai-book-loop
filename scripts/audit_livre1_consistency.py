from __future__ import annotations

import os
import urllib.request
from dataclasses import dataclass
from uuid import uuid4

from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.application.use_cases.ingest_document import IngestDocument
from book_loop.domain.models import Assertion, DocumentChunk, Evidence, SourceDocument
from book_loop.domain.temporal import AssertionTemporalContextStore, TemporalScope
from book_loop.infrastructure.llm.assertion_extractor import LLMAssertionExtractor
from book_loop.infrastructure.llm.gemini import GeminiProvider


CORPUS_URL = "https://raw.githubusercontent.com/Fkr-etu/M4ges/main/docs/story/livre_1/chapitre_{chapter:02d}.md"
BOOK_ID = "livre-1"
CHAPTERS = tuple(range(1, 9))


@dataclass
class AuditRepository:
    sources: list[SourceDocument]
    chunks: list[DocumentChunk]
    assertions: list[Assertion]
    evidence: list[Evidence]
    conflicts: list[object]

    def find_source_by_hash(self, *, book_id: str, content_hash: str) -> SourceDocument | None:
        return next(
            (
                source
                for source in self.sources
                if source.book_id == book_id and source.content_hash == content_hash
            ),
            None,
        )

    def save_source(self, source: SourceDocument) -> None:
        self.sources.append(source)

    def save_chunk(self, chunk: DocumentChunk) -> None:
        self.chunks.append(chunk)

    def save_assertion(self, assertion: Assertion) -> None:
        self.assertions.append(assertion)

    def save_evidence(self, evidence: Evidence) -> None:
        self.evidence.append(evidence)

    def list_assertions(self, *, book_id: str) -> list[Assertion]:
        return list(self.assertions)

    def save_conflict(self, conflict: object) -> None:
        self.conflicts.append(conflict)

    def list_conflicts(self, *, book_id: str) -> list[object]:
        return list(self.conflicts)


class InMemoryTemporalStore(AssertionTemporalContextStore):
    def __init__(self) -> None:
        self._scopes: dict[str, TemporalScope] = {}

    def get_temporal_scope(self, *, assertion_id: str) -> TemporalScope | None:
        return self._scopes.get(assertion_id)

    def save_temporal_scope(self, *, assertion_id: str, scope: TemporalScope) -> None:
        self._scopes[assertion_id] = scope


@dataclass(frozen=True)
class ChapterResult:
    chapter: int
    chunks: int
    assertions: int


def fetch_chapter(chapter: int) -> str:
    request = urllib.request.Request(
        CORPUS_URL.format(chapter=chapter),
        headers={"User-Agent": "book-loop-consistency-audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def build_extractor() -> LLMAssertionExtractor:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is required to run the real-corpus audit")
    model = os.environ.get("LLM_MODEL", "gemini-2.5-flash")
    provider = GeminiProvider(api_key=api_key, model=model)
    return LLMAssertionExtractor(provider=provider, language="fr")


def run_audit() -> tuple[list[ChapterResult], list[Assertion], list[object], InMemoryTemporalStore]:
    extractor = build_extractor()
    repository = AuditRepository([], [], [], [], [])
    temporal_store = InMemoryTemporalStore()
    ingestion = IngestDocument(
        repository=repository,
        extractor=extractor,
        chunk_size=1800,
        temporal_context_store=temporal_store,
    )

    chapter_results: list[ChapterResult] = []
    for chapter in CHAPTERS:
        content = fetch_chapter(chapter)
        result = ingestion.execute(
            book_id=BOOK_ID,
            name=f"Livre I — chapitre {chapter}",
            source_type="approved_chapter",
            content=content,
            metadata={"chapter_number": str(chapter), "chapter_version": "1"},
        )
        chapter_results.append(
            ChapterResult(
                chapter=chapter,
                chunks=len(result.chunks),
                assertions=len(result.assertions),
            )
        )

    conflicts = DetectConflicts(
        repository,
        temporal_context_store=temporal_store,
    ).execute(book_id=BOOK_ID)
    return chapter_results, repository.assertions, conflicts, temporal_store


def assertion_index(assertions: list[Assertion]) -> dict[str, Assertion]:
    return {assertion.id: assertion for assertion in assertions}


def chapter_for_assertion(assertion: Assertion, repository_sources: list[SourceDocument]) -> str:
    source = next(source for source in repository_sources if source.id == assertion.source_document_id)
    return source.metadata.get("chapter_number", "?")


def render_report(
    chapter_results: list[ChapterResult],
    assertions: list[Assertion],
    conflicts: list[object],
    temporal_store: InMemoryTemporalStore,
    sources: list[SourceDocument],
) -> str:
    by_id = assertion_index(assertions)
    lines = [
        "# Audit de cohérence — Livre I (corpus réel)",
        "",
        "Audit diagnostique produit à partir des assertions réellement extraites par `LLMAssertionExtractor`.",
        "Les chapitres sont récupérés depuis le dépôt public M4ges au moment de l'exécution.",
        "",
        "## Synthèse",
        "",
        f"- Chapitres analysés : {len(chapter_results)}",
        f"- Assertions extraites : {len(assertions)}",
        f"- Alertes de contradiction : {len(conflicts)}",
        "- Classification humaine : à effectuer sur les alertes ci-dessous",
        "",
        "## Extraction par chapitre",
        "",
        "| Chapitre | Chunks | Assertions |",
        "|---:|---:|---:|",
    ]
    lines.extend(
        f"| {item.chapter} | {item.chunks} | {item.assertions} |" for item in chapter_results
    )

    lines.extend(["", "## Alertes à examiner", ""])
    if not conflicts:
        lines.append("Aucune alerte produite par le détecteur.")
        return "\n".join(lines) + "\n"

    for index, conflict in enumerate(conflicts, start=1):
        left = by_id[conflict.left_assertion_id]
        right = by_id[conflict.right_assertion_id]
        left_scope = temporal_store.get_temporal_scope(assertion_id=left.id)
        right_scope = temporal_store.get_temporal_scope(assertion_id=right.id)
        lines.extend(
            [
                f"### {index}. `{left.subject} / {left.predicate}`",
                "",
                f"- A — chapitre {chapter_for_assertion(left, sources)}, story point {left_scope.position if left_scope else '?'} : `{left.statement}` → `{left.object}`",
                f"- B — chapitre {chapter_for_assertion(right, sources)}, story point {right_scope.position if right_scope else '?'} : `{right.statement}` → `{right.object}`",
                f"- Confiance : {left.confidence:.2f} / {right.confidence:.2f}",
                "- Qualification humaine : **à classer** — vraie contradiction / évolution narrative légitime / reformulation compatible / bruit",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    chapter_results, assertions, conflicts, temporal_store = run_audit()
    # Sources are reconstructed from the in-memory repository by re-running only the
    # metadata needed for reporting; the audit itself remains based on the real ingestion path.
    sources = [
        SourceDocument(
            id=assertion.source_document_id,
            book_id=BOOK_ID,
            name=f"Livre I — chapitre {chapter}",
            source_type="approved_chapter",
            content="audit-source",
            content_hash=uuid4().hex,
            metadata={"chapter_number": str(chapter), "chapter_version": "1"},
            version=1,
        )
        for assertion, chapter in []
    ]
    # Source ids are not exposed by run_audit; recover chapter metadata from assertion order.
    # The report only needs chapter labels, which are stored in the source ids through the
    # ingestion repository during the actual run. Reconstructing them is unnecessary when
    # there are no conflicts; for conflicts, use the assertion source name mapping below.
    raise RuntimeError("The script must be invoked through the CLI entry point below")


if __name__ == "__main__":
    # Kept explicit so the script remains an opt-in diagnostic and never runs in CI.
    chapter_results, assertions, conflicts, temporal_store = run_audit()
    # Re-fetch source metadata deterministically for report labels.
    source_by_id = {}
    for assertion in assertions:
        chapter = next(
            (chapter for chapter in CHAPTERS if f"chapitre {chapter}" in assertion.statement.lower()),
            None,
        )
        if chapter is not None:
            source_by_id[assertion.source_document_id] = SourceDocument(
                id=assertion.source_document_id,
                book_id=BOOK_ID,
                name=f"Livre I — chapitre {chapter}",
                source_type="approved_chapter",
                content="audit-source",
                content_hash=uuid4().hex,
                metadata={"chapter_number": str(chapter)},
                version=1,
            )
    print(f"Chapitres analysés : {len(chapter_results)}")
    print(f"Assertions extraites : {len(assertions)}")
    print(f"Alertes : {len(conflicts)}")
    for conflict in conflicts:
        left = assertion_index(assertions)[conflict.left_assertion_id]
        right = assertion_index(assertions)[conflict.right_assertion_id]
        left_scope = temporal_store.get_temporal_scope(assertion_id=left.id)
        right_scope = temporal_store.get_temporal_scope(assertion_id=right.id)
        print("-")
        print(f"A [{left_scope.position if left_scope else '?'}] {left.statement} -> {left.object}")
        print(f"B [{right_scope.position if right_scope else '?'}] {right.statement} -> {right.object}")
