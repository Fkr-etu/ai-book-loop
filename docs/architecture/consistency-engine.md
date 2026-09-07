# Corpus Consistency Engine

## Product intent

Book Loop protects the coherence of a long-lived book corpus. The system detects and explains possible contradictions; the author remains the decision-maker.

> L'IA propose, l'auteur décide.

## V1 boundary

The first consistency endpoint is deliberately conservative. It reuses the existing evidence-backed knowledge layer and deterministic `DetectConflicts` use case.

A consistency issue is currently a projection of a persisted `Conflict`:

```text
SourceDocument
    ↓
DocumentChunk
    ↓
Assertion ─────→ Evidence
    ↓
Conflict
    ↓
ConsistencyIssue (author-facing projection)
```

Only assertions sharing the same subject and predicate with different objects are flagged. Repeated analysis is idempotent because conflicts use deterministic IDs and the repository has a unique assertion-pair index.

## API

- `POST /api/books/{book_id}/consistency/analyze` runs the deterministic checks and returns the current issues.
- `GET /api/books/{book_id}/consistency/issues` reads the persisted issue state without writing.

Each issue exposes both assertions and their evidence excerpts so the UI can show *why* the system raised it. No endpoint automatically changes manuscript content or selects the winning assertion.

## Next increments

1. Canon-vs-corpus conflicts with explicit Canon evidence.
2. Character facts and attributes across chapters.
3. Temporal and chronology constraints.
4. Semantic/LLM-assisted conflicts only after deterministic precision is measured.
5. Async analysis and incremental re-analysis when corpus size requires it.
