# Product Scope

This document defines the **current product boundary**. It is intentionally short. Future phases, sequencing, and expansion criteria live in `docs/product/roadmap.md`.

## Current scope — Book MVP

The product is an agentic book-writing and review loop for a single author or small writing project.

### In scope

- Create a book project.
- Capture author intent, theme, lore, and explicit constraints.
- Generate a structured outline.
- Require explicit author approval before chapter generation.
- Generate chapters as bounded AI proposals.
- Lint and review each generated chapter.
- Retry within an explicit application-level budget.
- Preserve generated versions and review history.
- Produce an accepted chapter summary for continuity.
- Maintain the approved book state used by subsequent chapters.
- Support explicit approve / reject / revise decisions.
- Keep canonical knowledge separate from transient AI output.
- Persist the workflow state in SQLite for the current MVP.

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
Lint / review
  ↙       ↘
Retry    Accept
             ↓
     Accepted summary
             ↓
       Next chapter
```

## Canon MVP boundary

The next reusable capability is the smallest evidence-backed canonical model:

```text
Assertion → Evidence → Conflict → Review → CanonicalFact
```

For the MVP, Canon should remain focused on book continuity and review. It must not become a generic knowledge-management UI or require a graph/vector database.

Canonical rules:

- generated or extracted information is proposed until explicitly approved;
- canonical facts retain provenance;
- conflicts remain explicit until reviewed;
- review decisions are auditable;
- rejected/transient material is not used as canonical continuity memory.

## Explicitly out of scope for the current MVP

- PostgreSQL migration without a demonstrated production need.
- pgvector, embeddings, or generic RAG infrastructure.
- A full knowledge graph.
- Broad external documentation integrations.
- A generic documentation editor.
- Enterprise governance, SSO, billing infrastructure, or multi-tenant platform work.
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