# System Map

This document is the **navigation map for the current implementation**. It exists to reduce rediscovery, accidental duplication, and architecture drift—especially when work is performed by an AI agent.

## How to use this document

Before implementing a capability:

1. Start from `main` and read `AGENTS.md`.
2. Identify the business concept in this map.
3. Search the repository for the concept, existing interfaces, implementations, and tests.
4. Read the current implementation before designing a new one.
5. Reuse or extend the existing path when it already covers the capability.
6. Add a new abstraction only when the existing one cannot express the requirement cleanly.
7. Update this map when a new durable capability or architectural boundary is introduced.

**This map is a navigation aid, not a second source of business truth.** Detailed behavior belongs in the referenced code and focused architecture documents.

## Product north star

Book Loop helps creators keep a growing narrative universe coherent.

> **L'IA propose, l'auteur décide.**

The book/author workflow is the current product wedge. Canonical knowledge and evidence-backed consistency are the core technical differentiators. Generation is a means to create content; continuity and controlled evolution are the durable value.

## Runtime map

```text
Web / CLI
   |
   v
API routes / CLI commands
   |
   v
Application use cases + policies
   |
   +--------------------+
   |                    |
   v                    v
Domain models       Workflow orchestration
   |                    |
   |                    v
   |               ChapterWorkflow
   |                    |
   +---------+----------+
             |
             v
       Domain / ports
             ^
             |
       Infrastructure
       +-----------+-----------+
       |           |           |
     SQLite      LLM        Config

Knowledge / consistency path:

SourceDocument -> DocumentChunk -> Assertion -> Evidence
                                      |
                                      +-> Conflict -> ConsistencyIssue
                                      |
                                      +-> ReviewDecision -> CanonicalFact

New text validation:

chapter text -> assertion extraction -> CanonDiagnosticChecker
                                      |
                                      v
                           diagnostics against active Canon
```

## Where business behavior lives

| Concern | Canonical implementation | Tests / documentation |
|---|---|---|
| Book creation and lifecycle | `book_loop/application/use_cases/` | `tests/` + relevant use-case tests |
| Chapter generation | `book_loop/application/use_cases/` + `book_loop/workflows/` | chapter/workflow tests |
| Durable chapter execution | `ChapterWorkflow` + workflow-run store | `tests/` + `docs/architecture/chapter-workflow-recovery.md` |
| LLM capabilities | `book_loop/agents/` | agent tests / fakes |
| LLM provider abstraction | domain/application ports + infrastructure provider | provider/application tests |
| Canonical knowledge model | `book_loop/domain/models.py` + knowledge ports | `tests/test_canonical_*` |
| Assertion extraction | `book_loop/application/use_cases/extract_chapter_assertions.py` and extraction infrastructure | `tests/test_extract_chapter_assertions.py` |
| Assertion-vs-assertion conflict detection | `book_loop/application/use_cases/detect_conflicts.py` | conflict/canonical tests |
| New-text-vs-Canon validation | `book_loop/application/services/canon_validation.py` (`CanonDiagnosticChecker`) | `tests/test_canon_validation.py` |
| Unified consistency orchestration | `book_loop/application/use_cases/consistency_engine.py` (`UnifiedConsistencyEngine`) | `tests/test_consistency_engine.py` |
| Author-facing consistency API | `book_loop/application/use_cases/analyze_consistency.py` (`AnalyzeConsistency`) | consistency API/use-case tests |
| Canon review | `book_loop/application/use_cases/review_assertion.py` and related Canon use cases | `tests/test_canonical_review.py`, `tests/test_canonical_invariants.py` |
| Context assembly | `book_loop/application/services/context.py` (`ContextBuilder`) | `tests/test_canonical_context.py` and workflow tests |
| API composition and dependency wiring | `book_loop/infrastructure/container.py` | integration/API tests |
| Web UI | `web/src/app/`, `web/src/components/`, `web/src/services/` | `web/` Playwright E2E |

## Consistency architecture: current state

There are **multiple consistency mechanisms with different responsibilities**. Do not merge them by creating a second implementation of an existing rule.

### 1. `CanonDiagnosticChecker`

**Purpose:** validate a piece of new chapter text against the book's currently active Canon.

It extracts assertions from the supplied text, loads active canonical facts, and emits `Diagnostic` objects when the same subject/predicate has a different object.

This is already wired through `infrastructure/container.py` into the configured linguistic validation path.

**Do not replace it with a second Canon-vs-text detector.** If the unified consistency engine needs this capability, adapt the existing checker behind a detector interface rather than duplicating its rule.

### 2. `DetectConflicts`

**Purpose:** detect contradictions between persisted assertions in the corpus.

It is evidence-backed and persisted. It does not decide which assertion is true.

### 3. `UnifiedConsistencyEngine`

**Purpose:** compose independent consistency detectors and deduplicate their author-facing `ConsistencyIssue` results using stable issue IDs.

Current implementation is composable but **sequential**, not concurrent. Parallel execution is a future optimization for expensive detectors, not a current behavior.

### 4. `AnalyzeConsistency`

**Purpose:** application-facing entry point for the consistency API. It currently runs the unified engine and exposes existing issues without making read operations mutate state.

### 5. Canon review

**Purpose:** make an explicit human decision about proposed assertions and create/update canonical state. Detection must never silently promote an assertion to Canon.

## Authoritative sources

When sources disagree, use this priority order:

1. **Current code on `main`** for implemented behavior.
2. **Tests on `main`** for executable contracts and invariants.
3. **Focused architecture documentation** for design intent and boundaries.
4. **ADRs** for historical decisions and why they were made.
5. **README / product documentation** for orientation and product intent.
6. **PRs / commit history** for historical context only.
7. **Conversation history** as context, never as proof that a capability still exists.

A previous conversation can be stale. A previous PR can be superseded. Always verify against `main` before reimplementing something.

## Repository navigation

### Start here

- `AGENTS.md` — mandatory agent rules and definition of done.
- `README.md` — project orientation and documentation index.
- `docs/architecture/overview.md` — architecture responsibilities and runtime boundaries.
- `docs/architecture/principles.md` — invariants that must survive refactors.
- `docs/architecture/data-model.md` — persisted model and relationships.
- `docs/glossary.md` — project vocabulary.

### Workflow

- `docs/architecture/workflows.md`
- `docs/architecture/chapter-workflow-recovery.md`
- `docs/architecture/approved-chapter-canon-flow.md`
- `docs/architecture/generation-review-correction.md`

### Canon and knowledge

- `docs/architecture/canon-assertion-extraction.md`
- `docs/architecture/canonical-review.md`
- `docs/architecture/canonical-context.md`
- `docs/architecture/consistency-engine.md`
- `docs/architecture/document-ingestion.md`
- `docs/architecture/decisions/001-canonical-knowledge-engine.md`

### Frontend

The frontend is a client of backend contracts. It may own presentation state, but the backend remains authoritative for persisted book, workflow, Canon, and consistency state.

Relevant locations:

- `web/src/app/`
- `web/src/components/`
- `web/src/types/`
- `web/src/services/api.ts`
- `web/src/lib/useProjectStore.tsx`
- `web/tests/` or Playwright configuration and E2E specs

## Domain vocabulary that maps to code

- **Book** — top-level project aggregate.
- **Chapter** — versioned manuscript unit inside a book.
- **Outline** — structured chapter plan that gates generation.
- **SourceDocument** — persisted source material from which knowledge can be extracted.
- **DocumentChunk** — bounded source text unit used by extraction and evidence.
- **Assertion** — proposed structured claim extracted from source material.
- **Evidence** — provenance supporting an assertion.
- **Conflict** — persisted incompatibility between assertions.
- **ReviewDecision** — explicit acceptance/rejection/defer decision.
- **CanonicalFact** — approved source-of-truth assertion.
- **ConsistencyIssue** — author-facing projection of a consistency problem.
- **Diagnostic** — validation result, including linguistic and Canon diagnostics.
- **Agent** — focused LLM capability; not a business use case.
- **Workflow** — orchestration of multi-step execution and recovery.

## Extension rules

When adding a new consistency detector:

1. Define the detection responsibility precisely.
2. Search for existing rules that already detect the same relation.
3. Reuse existing extraction, evidence, and persistence paths where possible.
4. Return the shared `ConsistencyIssue` contract through the detector interface.
5. Keep truth/approval decisions outside detection.
6. Give the detector a stable identity strategy.
7. Add focused tests plus fusion/deduplication coverage.
8. Update `docs/architecture/consistency-engine.md` and this map.

When adding a new domain capability:

1. Search before designing.
2. Prefer an existing use case, port, model, or service over a parallel abstraction.
3. Keep deterministic rules in Python.
4. Keep LLM calls behind replaceable capabilities.
5. Persist decisions that affect future behavior.
6. Update the smallest number of canonical documents needed to explain the new behavior.

## Documentation maintenance rule

Documentation should answer one of four questions:

- **What exists?** → system map / architecture overview.
- **Why is it this way?** → ADR.
- **How does this workflow behave?** → focused architecture/workflow document.
- **How do I change or validate it?** → development/agent documentation.

If a proposed documentation change does not clearly answer one of these questions, prefer not to add another document.
