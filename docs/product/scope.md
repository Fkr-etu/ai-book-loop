# Product Scope

This document defines the **current product boundary**. Future phases, sequencing, and expansion criteria live in `docs/product/roadmap.md`.

## Current scope — Book MVP

The product is an author-focused narrative consistency and book-writing workflow. The Book is the first proving ground for a broader consistency engine, but the current user experience remains deliberately focused on the author/book wedge.

### In scope

- Create a book project.
- Capture author intent, theme, lore, and explicit constraints.
- Generate a structured outline.
- Require explicit author approval before chapter generation.
- Generate chapters as bounded AI proposals.
- Deterministically lint and linguistically validate generated chapters when configured.
- Review each validation-clean chapter with structured LLM feedback.
- Correct and retry within an explicit application-level budget.
- Preserve immutable generated versions and review history.
- Produce an accepted chapter summary for continuity.
- Maintain approved book state used by subsequent chapters.
- Maintain evidence-backed Canon assertions, conflicts, review decisions and canonical facts.
- Detect consistency issues through the current consistency pipeline.
- Keep canonical knowledge separate from transient AI output.
- Persist chapter workflow execution state in PostgreSQL in the current production architecture, with durable checkpoints and recovery semantics.
- Support idempotent chapter generation requests through workflow run identity and idempotency keys.
- Support explicit approve / reject / revise decisions at the application boundary.

### Core loop

```text
Author intent
     ↓
Outline proposal
     ↓
Author approval
     ↓
Chapter proposal
     ↓
Persisted version
     ↓
Lint / linguistic validation
     ↓
Consistency + structured review
  ↙                       ↘
Retry / correct          Accept
  ↓                         ↓
Review again             Summary
                            ↓
                     Approved chapter
                            ↓
                    Canon / next chapter
```

### Reliability boundary

The MVP distinguishes **content state** from **execution state**:

- chapter versions are immutable content history;
- `ChapterWorkflowRun` is durable execution state;
- the same `(book, chapter, idempotency_key)` does not intentionally execute a completed/terminal run again;
- recovery reuses a chapter version that was persisted before a process crash;
- current production persistence is PostgreSQL/Cloud SQL; SQLite remains useful only for isolated/local compatibility where explicitly supported by the implementation.

The current implementation serializes duplicate runs within one process. Cross-process worker claiming/leases are not yet part of the MVP.

## Canon and consistency MVP boundary

The evidence-backed Canon and consistency workflow is an implemented capability:

```text
SourceDocument / chapter content
             ↓
      Assertion + Evidence
             ↓
   Conflict / consistency detection
             ↓
       Human review
        ↙    ↓    ↘
    Reject Defer Accept
                   ↓
             CanonicalFact
```

Current ownership is explicit:

- `ExtractChapterAssertions` proposes assertions from source material;
- `DetectConflicts` detects persisted assertion-vs-assertion conflicts;
- `CanonDiagnosticChecker` detects new-text-vs-active-Canon contradictions;
- `UnifiedConsistencyEngine` composes consistency detectors and deduplicates stable issues;
- `ConsistencyIssue` is an author-facing projection, not Canon truth;
- review decisions remain the authority for Canon promotion.

Canonical rules:

- generated or extracted information is proposed until explicitly approved;
- canonical facts retain provenance;
- conflicts remain explicit until reviewed;
- review decisions are auditable;
- rejected/deferred/transient material is not canonical continuity memory;
- Canon is never mutated directly by an LLM or retrieval mechanism.

The MVP intentionally stops before a generic knowledge graph or mandatory vector/RAG infrastructure.

## Explicitly out of scope for the current MVP

- A generic knowledge graph.
- Mandatory pgvector, embeddings, or generic RAG infrastructure.
- Broad external documentation integrations.
- A generic documentation editor.
- Enterprise governance, SSO, billing infrastructure, or broad multi-tenant platform work.
- Cross-process distributed workflow leasing/worker orchestration.
- Complex multi-agent orchestration without a concrete workflow benefit.
- Broad transmedia/game-specific expansion unrelated to the core loop.
- Automatic, unsupervised Canon mutation or automatic conflict resolution.

## Future scope

The product roadmap contains the validated sequence for:

1. prove the Book loop with real authors;
2. strengthen Corpus Intelligence / Consistency Engine capabilities;
3. generalize Canon primitives where evidence warrants it;
4. build change-impact and regression analysis;
5. validate adjacent creator segments;
6. add integrations and SaaS governance;
7. test Documentation QA as a separate market;
8. add agentic resolution only after trust and value are demonstrated.

Do not treat future roadmap phases as current product requirements. Each expansion requires product evidence before implementation.
