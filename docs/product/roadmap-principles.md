# Roadmap Principles

This document records the sequencing decisions that apply to the product roadmap. The detailed feature phases remain in `docs/product/roadmap.md`; this document explains how to decide what should happen next.

## Current priority

The immediate priority is still the **Book MVP and its validation**. The Book is the first product and proving ground for the deeper canonical knowledge engine.

The next reusable technical capability is the **smallest Canon MVP**:

```text
Assertion → Evidence → Conflict → Review → CanonicalFact
```

This should be implemented inside the existing domain/application architecture and validated with tests before generalized infrastructure is introduced.

## Strategic sequence

```text
Book loop
   ↓
Canonical knowledge primitives
   ↓
Change impact / regression
   ↓
Documentation design partners
   ↓
Documentation QA MVP
   ↓
Existing-stack integrations
   ↓
SaaS governance
   ↓
Agentic resolution
   ↓
Enterprise infrastructure
```

The sequence is evidence-driven: passing a technical milestone is not sufficient to unlock the next product phase. The associated user and commercial hypothesis must also be validated.

## Infrastructure sequencing

Infrastructure follows measured need, not anticipation.

### SQLite

Keep SQLite for the current Book MVP and early Canon work. It is sufficient for the structured data and business rules being validated now.

### PostgreSQL

Move to PostgreSQL when the product has concrete production requirements such as meaningful multi-user concurrency, a deployed service with sustained writes, stronger transactional requirements, larger corpora, or operational requirements that justify a server database.

The migration should preserve the domain/application contracts and replace the persistence adapter rather than redesigning the domain.

### pgvector

Introduce pgvector only when semantic retrieval is a demonstrated bottleneck or has measurable product value. Examples include large corpora where structured retrieval is insufficient, or evaluation results showing that semantic retrieval materially improves evidence discovery, continuity checks, or regression detection.

Therefore:

```text
SQLite
  ↓ production / concurrency evidence
PostgreSQL
  ↓ semantic retrieval evidence
pgvector
```

PostgreSQL and pgvector are deliberately separate decisions.

## What not to build yet

Do not let future architecture drive current scope. Until the relevant evidence exists, avoid:

- PostgreSQL migration for its own sake;
- pgvector / embeddings;
- generic RAG infrastructure;
- a full knowledge graph;
- broad external integrations;
- enterprise governance;
- a generic documentation editor;
- complex multi-agent orchestration.

The principle is:

> **Do not pay platform complexity before the workflow has demonstrated the need for it.**

## Parallel work that is safe now

While roadmap and strategy work is being refined, implementation can proceed independently on low-collision foundations:

- Canon domain models;
- canonical state transition rules;
- provenance and evidence invariants;
- conflict representation;
- review decisions;
- dependency primitives;
- unit/integration tests for approval boundaries;
- CI quality improvements;
- LLM usage and cost instrumentation.

These streams should avoid changing the product roadmap or introducing infrastructure that has not yet been justified.

## Decision gates

A new phase or major infrastructure component should be unlocked only when the relevant evidence supports it:

1. **Value** — the workflow solves a painful problem.
2. **Trust** — users can verify findings and canonical changes.
3. **Frequency** — the workflow recurs often enough to matter.
4. **Integration** — it fits existing sources of truth.
5. **Economics** — the value supports inference and infrastructure costs.

If a gate fails, revisit the workflow or ICP instead of compensating with more technology.
