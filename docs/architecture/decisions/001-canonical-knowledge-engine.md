# ADR 001 — Canonical Knowledge Engine as the Core Abstraction

- **Status:** Accepted
- **Date:** 2026-09-02

## Context

The product starts with an AI-assisted book-writing workflow, but the strategic value is broader than text generation. A long-lived project needs a trustworthy representation of what is known, what is disputed, what was approved, and where each assertion came from.

Books are the first proving ground because they naturally contain characters, facts, relationships, events, timelines, rules, and evolving source material. The same problem appears later in technical and company documentation: a corpus contains claims that can become contradictory or stale when new content is introduced.

The system therefore needs an explicit distinction between generated proposals and approved knowledge.

## Decision

Treat **Canon** as a first-class domain concept and the long-term core abstraction of the product.

The book remains the first product experience and MVP. Canon is not exposed as an abstract generic product prematurely; instead, the book workflow is used to prove the underlying model and validation loop.

The conceptual lifecycle is:

```text
Source documents
      ↓
   Extraction
      ↓
   Assertions
      ↓
Evidence / conflicts / confidence
      ↓
 Human review & decision
      ↓
     Canon
      ↓
Generation / QA / impact analysis
```

A canonical item must be traceable to its supporting evidence and approval decision. LLM output, extracted assertions, drafts, and reviews are proposals or evidence; they do not silently become canonical.

## Canonical primitives

The model should evolve toward reusable primitives such as:

- **SourceDocument** — a document or source from which knowledge is derived;
- **Assertion** — a proposed statement about an entity, relationship, event, rule, or state;
- **Evidence** — source-level support for an assertion, with provenance;
- **Conflict** — competing assertions that cannot all be true under the same interpretation;
- **CanonicalFact** — an approved assertion accepted as part of the project's source of truth;
- **ReviewDecision** — the human or policy decision that accepted, rejected, or deferred a proposal;
- **Provenance** — enough source and location information to explain why a fact exists;
- **Confidence** — an explicit signal about extraction or inference confidence, never a substitute for approval;
- **Dependency** — a relation between claims and content whose validity can affect downstream material.

The exact persistence schema is intentionally deferred until the first concrete book use cases establish the required invariants.

## Invariants

1. Canon is the source of truth for validated knowledge.
2. Generated or extracted information is non-canonical until explicitly approved.
3. Every canonical fact must have provenance.
4. Historical decisions and prior versions must remain auditable.
5. Contradictions must be represented rather than silently resolved by the model.
6. Deterministic authorization, sequencing, and state transitions remain application responsibilities.
7. Retrieval is an implementation concern; a vector index must never become the source of truth.
8. The model must work for books without forcing the book UX to become a generic knowledge-management interface.

## Consequences

### Positive

- Gives the product a durable abstraction beyond book generation.
- Makes continuity and correctness testable independently from prose generation.
- Enables evidence-backed review instead of opaque LLM judgments.
- Creates a path from book continuity to documentation regression analysis.
- Allows future semantic retrieval to optimize access without changing the source of truth.

### Negative / trade-offs

- Adds domain concepts beyond the current minimal Book/Chapter model.
- Requires careful provenance and versioning design.
- Human review remains necessary for high-value canonical decisions.
- The abstraction should not be implemented wholesale before the book use cases demonstrate which invariants matter.

## Rejected alternatives

### Treat the prompt context as the canon

Rejected because prompt text is ephemeral, difficult to audit, and cannot reliably represent conflicts or provenance.

### Use a vector database as the canonical store

Rejected because embeddings optimize retrieval, not truth, provenance, approval, or deterministic state transitions.

### Build a generic knowledge-management product first

Rejected because it would dilute the book MVP and force premature generalization.

## Implementation direction

The next implementation step is not a full knowledge graph or vector database. It is to introduce the smallest domain model needed to validate canonical review inside the book workflow:

1. source/reference metadata;
2. assertions extracted from book material;
3. evidence and provenance;
4. conflict detection;
5. explicit approval/rejection;
6. persistence and audit history;
7. consumption of approved canonical facts by chapter QA/generation.

Only after these primitives prove useful should semantic retrieval, richer relationship graphs, and external documentation integrations be added.