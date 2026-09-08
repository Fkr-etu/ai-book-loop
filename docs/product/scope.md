# Product Scope

This document defines the **current product boundary**. Future sequencing and expansion criteria live in `docs/product/roadmap.md`.

## Current scope — Book MVP

The product is an author-focused narrative consistency and book-writing workflow. The Book is the first proving ground for a broader consistency engine; the current user experience remains focused on the author/book wedge.

### In scope

- Create a book project.
- Capture author intent, theme, lore and explicit constraints.
- Generate and approve a structured outline.
- Generate chapters as bounded AI proposals.
- Deterministically lint and linguistically validate generated chapters when configured.
- Review validation-clean chapters with structured feedback.
- Correct and retry within an explicit application-level budget.
- Preserve immutable generated versions and review history.
- Produce accepted chapter summaries for continuity.
- Maintain approved book state used by subsequent chapters.
- Maintain evidence-backed Canon assertions, conflicts, review decisions and canonical facts.
- Detect consistency issues through the current consistency pipeline.
- Keep canonical knowledge separate from transient AI output.
- Persist workflow execution state in PostgreSQL in the production architecture, with durable checkpoints and recovery semantics.
- Support idempotent chapter generation through workflow-run identity and idempotency keys.
- Support explicit approve / reject / revise decisions at the application boundary.
- Support the current creator subscription model through Stripe billing and bounded workflow capacity.

## Core loop

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

## Reliability boundary

The MVP distinguishes **content state** from **execution state**:

- chapter versions are immutable content history;
- `ChapterWorkflowRun` is durable execution state;
- the same `(book, chapter, idempotency_key)` does not intentionally execute a completed/terminal run again;
- recovery reuses persisted chapter state after a process crash;
- production persistence is PostgreSQL/Cloud SQL; SQLite is limited to isolated/local compatibility where explicitly supported;
- duplicate-run serialization is currently process-local; cross-process worker claiming/leases are not part of the MVP.

## Canon and consistency boundary

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
- Mandatory pgvector, embeddings or generic RAG infrastructure.
- Broad external documentation integrations.
- A generic documentation editor.
- Enterprise governance, SSO or broad multi-tenant platform work.
- Cross-process distributed workflow leasing/worker orchestration.
- Complex multi-agent orchestration without a concrete workflow benefit.
- Broad transmedia/game-specific expansion unrelated to the core loop.
- Automatic, unsupervised Canon mutation or automatic conflict resolution.

Billing infrastructure is **not** out of scope anymore: the current creator billing and capacity foundation is implemented. Enterprise billing/governance remains out of scope.

## Future scope

The roadmap sequence is:

1. prove the Book loop with real authors;
2. strengthen consistency and change-impact capabilities;
3. generalize Canon primitives where evidence warrants it;
4. validate adjacent creator segments;
5. add integrations and mature the creator SaaS;
6. test Documentation QA as a separate market;
7. add agentic resolution only after trust and value are demonstrated.

Do not treat future roadmap phases as current product requirements. Each expansion requires product evidence before implementation.
