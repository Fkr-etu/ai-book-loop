# Product Scope

This document defines the **current product boundary**. Future phases, sequencing, and expansion criteria live in `docs/product/roadmap.md`.

## Current scope — Book MVP

The product is an agentic book-writing and review loop for a single author or small writing project.

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
- Keep canonical knowledge separate from transient AI output.
- Persist chapter workflow execution state in SQLite so in-progress runs can resume after process restart.
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
Structured review
  ↙       ↘
Retry    Accept
  ↓          ↓
Correct   Summary
  └──→ Review
             ↓
       Approved chapter
             ↓
       Next chapter
```

### Reliability boundary

The MVP now distinguishes **content state** from **execution state**:

- chapter versions are immutable content history;
- `ChapterWorkflowRun` is durable execution state;
- the same `(book, chapter, idempotency_key)` does not intentionally execute the completed run again;
- recovery reuses a chapter version that was persisted before a process crash.

The current implementation serializes duplicate runs within one process. Cross-process worker claiming/leases are not yet part of the MVP.

## Canon MVP boundary

The evidence-backed Canon workflow is now an implemented MVP capability:

```text
SourceDocument
      ↓
Assertion + Evidence
      ↓
Conflict detection
      ↓
Human/application review
   ↙      ↓       ↘
Reject  Defer    Accept
                  ↓
            CanonicalFact
```

Canonical rules:

- generated or extracted information is proposed until explicitly approved;
- canonical facts retain provenance;
- conflicts remain explicit until reviewed;
- review decisions are auditable;
- rejected/deferred/transient material is not canonical continuity memory;
- Canon is never mutated directly by an LLM or retrieval mechanism.

The MVP intentionally stops before a generic knowledge graph or mandatory vector/RAG infrastructure.

## Explicitly out of scope for the current MVP

- PostgreSQL migration without a demonstrated production need.
- Mandatory pgvector, embeddings, or generic RAG infrastructure.
- A full knowledge graph.
- Broad external documentation integrations.
- A generic documentation editor.
- Enterprise governance, SSO, billing infrastructure, or multi-tenant platform work.
- Cross-process distributed workflow leasing/worker orchestration.
- Complex multi-agent orchestration without a concrete workflow benefit.
- Broad transmedia/game-specific expansion unrelated to the core loop.

## Future scope

The product roadmap contains the validated sequence for:

1. excellent Book loop;
2. generalized Canon primitives;
3. change-impact and regression analysis;
4. documentation design partners;
5. Documentation QA;
6. integrations and SaaS governance;
7. agentic resolution;
8. enterprise infrastructure.

Do not treat future roadmap phases as current product requirements. Each expansion requires product evidence before implementation.
