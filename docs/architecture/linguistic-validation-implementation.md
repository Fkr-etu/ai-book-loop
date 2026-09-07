# Linguistic validation — implementation history

> **Historical implementation note.** This document records the staged introduction of linguistic validation. It is not the current architecture source of truth. For current workflow behavior, use `workflows.md`; for the current diagnostic/consistency architecture, use `consistency-engine.md` and the Canon documentation.

## What this implementation established

- provider-neutral `Diagnostic` contract with category, severity, source, offsets, suggestions, confidence and provenance metadata;
- explicit `NO_ISSUES_FOUND`, `ISSUES_FOUND` and `CHECK_NOT_AVAILABLE` states;
- `LinguisticValidationService` aggregation and deterministic fusion;
- LanguageTool HTTP adapter and preserved rule IDs/replacement suggestions;
- explicit handling of provider/network failure;
- optional spaCy structural detection and lazy model loading;
- labelled French evaluation corpus and detector-agnostic evaluation metrics.

## Current boundary

Linguistic validation is now part of the implemented validation surface and is wired through the application configuration. It remains distinct from Canon consistency detection.

- Linguistic validation produces diagnostics about language/structure.
- `CanonDiagnosticChecker` compares new text with active Canon facts.
- `DetectConflicts` detects contradictions between persisted assertions.
- `UnifiedConsistencyEngine` composes consistency detectors into author-facing `ConsistencyIssue` results.

None of these systems silently promotes information to Canon.

## Configuration

```text
LINGUISTIC_CHECKER=disabled
LANGUAGE_TOOL_URL=http://localhost:8010
LINGUISTIC_LANGUAGE=fr
SPACY_MODEL=fr_core_news_sm
```

The checker remains configurable and conservative. The base application does not require the optional spaCy model.

## Evaluation

The corpus lives at `tests/fixtures/linguistic_corpus.json`. It remains version-controlled so detector behavior and false-positive cost can be evaluated reproducibly.

## Where to read current behavior

- `docs/architecture/overview.md` — system responsibilities;
- `docs/architecture/workflows.md` — generation/validation workflow;
- `docs/architecture/consistency-engine.md` — consistency detector architecture;
- `docs/architecture/canon-assertion-extraction.md` — assertion lifecycle.
