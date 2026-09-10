from __future__ import annotations

import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.application.use_cases.ingest_document import IngestDocument
from book_loop.domain.models import Assertion, DocumentChunk, Evidence, SourceDocument
from book_loop.domain.temporal import AssertionTemporalContextStore, TemporalScope
from book_loop.infrastructure.llm.assertion_extractor import LLMAssertionExtractor
from book_loop.infrastructure.llm.gemini import GeminiProvider


CORPUS_URL = "https://github.com/Fkr-etu/M4ges/raw/main/docs/story/livre_1/chapitre_{chapter:02d}.md"
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


class InMemoryTemporalStore:
    def __init__(self) -> None:
        self._scopes: dict[str, TemporalScope] = {}

    def get_temporal_scope(self, *, assertion_id: str) -> TemporalScope | None:
        return self._scopes.get(assertion_id)

    def save_temporal_scope(self, *, assertion_id: str, scope: TemporalScope) -> None:
        self._scopes[assertion_id] = scope


@dataclass(frozen=True)
class AuditResult:
    chapter_results: tuple[tuple[int, int, int], ...]
    repository: AuditRepository
    temporal_store: InMemoryTemporalStore
    conflicts: tuple[object, ...]


def fetch_chapter(chapter: int) -> str:
    url = CORPUS_URL.format(chapter=chapter)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "book-loop-consistency-audit/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"Unable to fetch Livre I chapter {chapter} (HTTP {exc.code}): {url}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Unable to fetch Livre I chapter {chapter}: {url} ({exc.reason})"
        ) from exc


def build_extractor() -> LLMAssertionExtractor:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is required to run the real-corpus audit")
    model = os.environ.get("LLM_MODEL", "gemini-3.5-flash")
    provider = GeminiProvider(api_key=api_key, model=model)
    return LLMAssertionExtractor(provider=provider, language="fr")


def run_audit() -> AuditResult:
    corpus = {chapter: fetch_chapter(chapter) for chapter in CHAPTERS}
    extractor = build_extractor()
    repository = AuditRepository([], [], [], [], [])
    temporal_store = InMemoryTemporalStore()
    ingestion = IngestDocument(
        repository=repository,
        extractor=extractor,
        chunk_size=1800,
        temporal_context_store=temporal_store,
    )

    chapter_results: list[tuple[int, int, int]] = []
    for chapter in CHAPTERS:
        result = ingestion.execute(
            book_id=BOOK_ID,
            name=f"Livre I — chapitre {chapter}",
            source_type="approved_chapter",
            content=corpus[chapter],
            metadata={"chapter_number": str(chapter), "chapter_version": "1"},
        )
        chapter_results.append((chapter, len(result.chunks), len(result.assertions)))

    conflicts = DetectConflicts(
        repository,
        temporal_context_store=temporal_store,
    ).execute(book_id=BOOK_ID)
    return AuditResult(
        chapter_results=tuple(chapter_results),
        repository=repository,
        temporal_store=temporal_store,
        conflicts=tuple(conflicts),
    )


def render_report(result: AuditResult) -> str:
    by_id = {assertion.id: assertion for assertion in result.repository.assertions}
    source_by_id = {source.id: source for source in result.repository.sources}
    lines = [
        "# Audit de cohérence — Livre I (corpus réel)",
        "",
        "Audit diagnostique produit à partir des assertions réellement extraites par `LLMAssertionExtractor`.",
        "Les chapitres sont récupérés depuis le dépôt public M4ges au moment de l'exécution.",
        "",
        "## Synthèse",
        "",
        f"- Chapitres analysés : {len(result.chapter_results)}",
        f"- Assertions extraites : {len(result.repository.assertions)}",
        f"- Alertes de contradiction : {len(result.conflicts)}",
        "- Classification humaine : à effectuer sur les alertes ci-dessous",
        "",
        "## Extraction par chapitre",
        "",
        "| Chapitre | Chunks | Assertions |",
        "|---:|---:|---:|",
    ]
    lines.extend(f"| {chapter} | {chunks} | {assertions} |" for chapter, chunks, assertions in result.chapter_results)
    lines.extend(["", "## Alertes à examiner", ""])

    if not result.conflicts:
        lines.append("Aucune alerte produite par le détecteur.")
        return "\n".join(lines) + "\n"

    for index, conflict in enumerate(result.conflicts, start=1):
        left = by_id[conflict.left_assertion_id]
        right = by_id[conflict.right_assertion_id]
        left_scope = result.temporal_store.get_temporal_scope(assertion_id=left.id)
        right_scope = result.temporal_store.get_temporal_scope(assertion_id=right.id)
        left_chapter = source_by_id[left.source_document_id].metadata.get("chapter_number", "?")
        right_chapter = source_by_id[right.source_document_id].metadata.get("chapter_number", "?")
        lines.extend(
            [
                f"### {index}. `{left.subject} / {left.predicate}`",
                "",
                f"- A — chapitre {left_chapter}, story point {left_scope.position if left_scope else '?'} : `{left.statement}` → `{left.object}`",
                f"- B — chapitre {right_chapter}, story point {right_scope.position if right_scope else '?'} : `{right.statement}` → `{right.object}`",
                f"- Confiance : {left.confidence:.2f} / {right.confidence:.2f}",
                "- Qualification humaine : **à classer** — vraie contradiction / évolution narrative légitime / reformulation compatible / bruit",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    try:
        result = run_audit()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    report = render_report(result)
    print(report, end="")


if __name__ == "__main__":
    main()
