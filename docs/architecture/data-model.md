# Data Model

This document describes the conceptual persisted state. The implementation remains the source of truth for exact serialization details.

## Book

A book contains the author's creative inputs and the generated state needed to continue writing.

Core inputs:

- `id`
- `owner_id`
- `title`
- `theme`
- `author_idea`
- `lore`
- `constraints`

Generated/approval state includes the structured outline, its approval status, and chapters.

`owner_id` identifies the authenticated owner of an API-created book. Authorization is an application/API concern; it is not delegated to the LLM workflow.

## Outline

The outline is structured rather than an opaque text blob.

An `Outline` contains one or more `OutlineChapter` entries. Each entry has:

- `number` — positive, sequential chapter number starting at `1`;
- `title`;
- `objective` — the writing objective used by chapter generation;
- `synopsis` — optional chapter synopsis.

The domain validates that chapter numbers are consecutive. The outline must be explicitly approved before chapter generation.

## Chapter

A chapter is identified within a book by its sequence number and contains at least a title and objective.

The current workflow also tracks:

- `status`;
- `current_version` — the accepted/current generated attempt number;
- `summary` — the canonical continuity summary when the chapter has been accepted.

Generation attempts are persisted separately through repository version history. Reviews are also persisted against the corresponding chapter attempt, so rejected drafts are not silently overwritten.

Relevant statuses include `draft`, `proposed`, `approved`, `rejected`, `canonical`, and `needs_review`. The chapter loop currently sets an accepted generated chapter to `approved`; exhausted retries terminate without producing a canonical summary.

## Chapter review

A `SceneReview` contains:

- `score` — numeric score from `0` to `10`, including fractional values such as `8.5`;
- `approved` — reviewer assessment;
- `issues`;
- `suggestions`.

The application review policy converts the review into a workflow decision. The configured threshold and retry budget remain application policy.

## Canonical context

Canonical context is built from persisted author/book information and accepted summaries of previous chapters. For a chapter generation run, the current context contains:

- author idea;
- theme;
- lore;
- global structured outline;
- global constraints;
- summaries for chapters preceding the current chapter;
- current chapter objective.

This bounded context provides continuity without requiring the entire chapter history to be resent to the LLM on every call.

Rejected attempts and transient review output are not treated as canonical continuity memory.

## Canonical knowledge model — target evolution

The product is evolving toward a first-class canonical knowledge model. The smallest useful conceptual primitives are:

### SourceDocument

A document or source from which knowledge can be derived. It should retain stable identity and enough metadata to locate the relevant source/version.

### Assertion

A proposed claim extracted or inferred from a source, such as a character attribute, relationship, event, timeline fact, world rule, or documentation statement.

Assertions are **not canonical by default**.

### Evidence / Provenance

Evidence connects an assertion to its supporting source and location. Provenance should answer where the assertion came from and which source version supported it.

### Conflict

A representation of competing assertions that cannot all be accepted under the same interpretation. Conflicts must remain visible until resolved; the LLM must not silently choose a winner.

### ReviewDecision

The decision that accepts, rejects, or defers an assertion/canonical change. Decisions should remain auditable and associated with the actor, timestamp, and relevant evidence where the implementation supports them.

### CanonicalFact

An approved assertion that belongs to the project's source of truth. A canonical fact must retain provenance and an approval trail.

### Confidence

A signal about extraction or inference quality. Confidence can help prioritize review but **does not itself make an assertion canonical**.

### Dependency

A relationship indicating that the validity of one claim or content item depends on another claim. This is the basis for future change-impact and regression analysis.

The exact schema is intentionally deferred. We should implement these concepts incrementally, beginning with the subset required to validate book continuity and document review.

## Canonical state lifecycle

The conceptual lifecycle is:

```text
RAW SOURCE
    ↓
EXTRACTED ASSERTIONS
    ↓
EVIDENCE / CONFLICTS
    ↓
REVIEW DECISION
    ↓
CANONICAL FACTS
    ↓
GENERATION / QA
```

The important boundary is between **proposed knowledge** and **approved knowledge**. Downstream generation and validation should consume canonical facts by default.

## State ownership

- Author inputs are persisted as book state.
- Outline approval is application state and changes only through explicit application/API actions.
- Chapter drafts are generated by the Writer agent and persisted as versioned attempts.
- Reviews are generated by the Reviewer agent and persisted per attempt.
- Accepted summaries are generated by the Summarizer agent and persisted on the chapter as continuity data.
- Canonical knowledge changes are explicit application actions backed by evidence and review decisions.
- Agents may extract, compare, classify, or propose knowledge changes, but do not own canonical state transitions.
- The workflow coordinates these transitions but does not become the source of truth for domain state.
- SQLite is an implementation detail of persistence.

## Retrieval rule

Semantic search, embeddings, vector indexes, full-text search, or graph traversal may later improve how canonical knowledge is retrieved. They are **retrieval mechanisms, not canonical stores**. The authoritative state remains structured, persisted, provenance-aware, and reviewable.

## Evolution rule

If a persisted field or invariant changes, update this document in the same change and add an ADR when the change affects an architectural decision.
