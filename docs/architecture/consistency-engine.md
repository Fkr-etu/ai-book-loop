# Corpus Consistency Engine

## Product intent

Book Loop protects the coherence of a long-lived book corpus. The system detects and explains possible contradictions; the author remains the decision-maker.

> **L'IA propose, l'auteur décide.**

The consistency engine is therefore a **detection and explanation layer**, not an autonomous truth engine. It may surface a conflict, but it must not silently choose which statement is true or mutate Canon.

## Current architecture

The repository already contains more than one consistency mechanism. They solve different problems and must remain distinct:

```text
                         UnifiedConsistencyEngine
                                  |
                   +--------------+--------------+
                   |                             |
          AssertionConsistencyDetector     future detectors
                   |
             DetectConflicts
                   |
        Assertion ↔ Assertion

New chapter text
      |
      v
CanonDiagnosticChecker
      |
Assertion extraction + active Canon
      |
Assertion ↔ Canon
```

The first path is the current author-facing corpus consistency engine. The second path is an existing chapter-validation mechanism used during linguistic validation. **Do not implement a second Canon-vs-text detector.** If the unified engine needs that capability, adapt the existing `CanonDiagnosticChecker` behind the shared detector contract.

## Existing implementations

### `DetectConflicts`

Location: `book_loop/application/use_cases/detect_conflicts.py`

Responsibility: detect contradictions between persisted assertions in one book.

Current V1 rule: two non-rejected assertions conflict when they have the same normalized subject and predicate but different normalized objects.

Properties:

- evidence-backed because assertions originate from persisted source material;
- persisted through the knowledge repository;
- deterministic conflict IDs;
- idempotent re-analysis;
- does not decide truth.

### `CanonDiagnosticChecker`

Location: `book_loop/application/services/canon_validation.py`

Responsibility: compare assertions extracted from **new chapter text** with the book's active `CanonicalFact` records and emit `Diagnostic` objects for contradictions.

This checker is already wired by `book_loop/infrastructure/container.py` into the configured linguistic validation path and has dedicated tests in `tests/test_canon_validation.py`.

Its source of truth remains the existing checker. Any future consistency-engine integration should compose or adapt it rather than copy its comparison logic.

### `AssertionConsistencyDetector`

Location: `book_loop/application/use_cases/assertion_consistency_detector.py`

Responsibility: adapt the existing persisted `DetectConflicts` behavior to the shared consistency-detector contract and project conflicts into `ConsistencyIssue` objects.

It is an adapter, not a replacement for `DetectConflicts`.

### `UnifiedConsistencyEngine`

Location: `book_loop/application/use_cases/consistency_engine.py`

Responsibility: compose registered detectors and deduplicate their `ConsistencyIssue` results using stable issue IDs.

Current execution is **sequential**. Detectors are architecturally independent/composable, but they are not currently executed concurrently. Parallel execution may be considered later when expensive semantic/LLM detectors exist and their persistence/session boundaries are safe.

### `AnalyzeConsistency`

Location: `book_loop/application/use_cases/analyze_consistency.py`

Responsibility: application entry point for consistency analysis. It currently runs `UnifiedConsistencyEngine` and preserves the existing API contract.

`list_existing()` reads existing conflict state without creating a second detection path.

## Data flow

```text
SourceDocument
    ↓
DocumentChunk
    ↓
Assertion ─────────→ Evidence
    ↓
Conflict
    ↓
ConsistencyIssue

Assertion
    ↓
ReviewDecision
    ↓
CanonicalFact
```

The important distinction is:

- **Assertion** = proposed claim extracted from source material.
- **Conflict** = persisted incompatibility between assertions.
- **ConsistencyIssue** = author-facing projection used by the consistency surface.
- **CanonicalFact** = approved source-of-truth claim.
- **Diagnostic** = validation result; Canon diagnostics are one existing validation path.

## API

- `POST /api/books/{book_id}/consistency/analyze` runs deterministic consistency analysis and returns current issues.
- `GET /api/books/{book_id}/consistency/issues` reads current issue state without performing a write.

Each issue exposes both assertions and their evidence excerpts so the UI can show *why* the system raised it. No consistency endpoint automatically changes manuscript content or selects the winning assertion.

## Idempotency and identity

The consistency layer must remain safe to run repeatedly.

- Persisted conflicts use deterministic IDs derived from the book and assertion pair.
- The persistence layer protects active assertion-pair uniqueness.
- The author-facing projection must use a stable issue identity so detector fusion does not produce duplicate issues.
- Analysis must not create a second logically equivalent conflict on every request.

When adding a detector, define its identity strategy explicitly and add a regression test for repeated analysis.

## Precision-first strategy

The engine should optimize for **useful precision before broad recall**. A flood of weak consistency warnings is worse than a smaller set of evidence-backed issues.

The intended progression is:

1. deterministic assertion conflicts;
2. existing Canon-vs-new-text diagnostics integrated without duplication;
3. richer structured facts such as character attributes and relationships;
4. chronology and temporal constraints;
5. semantic/LLM-assisted detection where deterministic rules cannot express the relation;
6. incremental and asynchronous analysis when corpus size requires it.

LLM-assisted detection must expose evidence, confidence, and provenance and must remain a proposal. It must not become an implicit approval mechanism.

## Detector contract

A consistency detector should:

- accept a book identifier and inspect authoritative persisted state as needed;
- return the shared `ConsistencyIssue` contract;
- have one clearly defined detection responsibility;
- preserve provenance/evidence references;
- use stable identities;
- avoid mutating Canon;
- be independently testable;
- be composable by `UnifiedConsistencyEngine`.

The engine owns **composition and deduplication**. A detector owns **its detection rule**. Canon review owns **the truth/approval decision**.

## Adding a detector safely

Before adding one:

1. Search the repository for the business concept and synonyms.
2. Search for validators, diagnostics, conflict rules, repository queries, and existing tests.
3. Inspect `CanonDiagnosticChecker` and `DetectConflicts` whenever the new detector concerns continuity or contradictions.
4. Reuse existing extraction/evidence/persistence paths.
5. Decide whether the requirement is a new rule or a new projection of an existing rule.
6. Implement the smallest detector-specific logic.
7. Register it with `UnifiedConsistencyEngine`.
8. Add detector-level tests and fusion/deduplication tests.
9. Update `docs/architecture/system-map.md` and this document.

## What the engine does not do

The consistency engine does not:

- decide which conflicting assertion is true;
- silently rewrite manuscript text;
- silently promote extracted knowledge to Canon;
- replace human review;
- treat embeddings or an LLM as the source of truth;
- duplicate existing validation rules merely to expose them through another surface.

## Future increments

### Canon-vs-corpus integration

Expose the existing `CanonDiagnosticChecker` capability through the unified detector contract without duplicating its rule or changing its current validation behavior.

### Structured character and relationship facts

Introduce explicit predicates/relations only where the book use cases demonstrate stable invariants worth enforcing.

### Temporal reasoning

Add date/order/duration constraints with explicit representations rather than relying on free-form semantic guesses.

### Semantic / LLM detection

Use an LLM only for relations that deterministic logic cannot reliably express. Every finding should retain evidence and confidence and remain reviewable.

### Incremental / async analysis

Only introduce asynchronous or parallel execution when corpus size or detector cost makes it necessary. The current detector loop is sequential by design.
