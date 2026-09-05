# Data Model

This document describes the persisted state and its ownership boundaries. The implementation remains the source of truth for exact serialization details.

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

The chapter stores the accepted/current state:

- `status`;
- `current_version` — the accepted generated attempt number;
- `summary` — the accepted continuity summary.

Generated attempts are persisted separately through immutable chapter-version history. Reviews are persisted against the corresponding chapter attempt, so rejected drafts are not silently overwritten.

Relevant statuses include `draft`, `proposed`, `approved`, `rejected`, `canonical`, and `needs_review`. The chapter workflow sets an accepted generated chapter to `approved`; exhausted retries end without advancing `current_version` or creating an accepted summary.

## Chapter versions

A chapter version is identified by `(book_id, chapter_number, version)` and is immutable after persistence. Version numbers start at `1` and increase for retries/corrections.

The workflow reserves an attempt before calling an LLM. On recovery, an already persisted version is reused rather than generated again. This is the main protection against duplicate generation after a process crash.

## Workflow run

Chapter execution state is persisted separately from `BookState` so workflow progress can survive process restart.

`ChapterWorkflowRun` contains:

- `id` — durable run identifier;
- `book_id`;
- `chapter_number`;
- `idempotency_key`;
- `status` — `running`, `completed`, or `needs_review`;
- `step` — `write`, `review`, `correct`, or `summarize`;
- `attempt` — current chapter version/attempt;
- `draft` — current draft text;
- `review` — current `SceneReview`, when available;
- `decision` — application review decision, when available;
- `summary` — accepted summary, when available.

A durable run is uniquely identified by `(book_id, chapter_number, idempotency_key)`. Repeating a completed or terminal run with the same key does not invoke agents again.

`GenerateChapter` derives a stable default idempotency key from the next expected chapter version. Callers can supply an explicit key when request-level idempotency is required.

The workflow store is an infrastructure concern. Production wiring uses `SQLiteWorkflowRunStore`; isolated tests/lightweight callers can use `InMemoryWorkflowRunStore`.

## Chapter review

A `SceneReview` contains:

- `score` — numeric score from `0` to `10`, including fractional values such as `8.5`;
- `approved` — reviewer assessment;
- `issues`;
- `suggestions`.

The application review policy converts the review into a workflow decision. The configured threshold and retry budget remain application policy.

## Diagnostics and linguistic validation

Chapter validation may produce structured diagnostics with a category, severity, source, message, offsets, suggestions and confidence. Blocking linguistic `ERROR` diagnostics prevent the LLM reviewer from being called; non-blocking diagnostics are passed to the reviewer.

Canon diagnostics remain distinct from linguistic diagnostics and are not sent through the linguistic contextualizer.

## Canonical knowledge

### SourceDocument

A document or source from which knowledge can be derived. It retains stable identity and enough metadata to locate the relevant source/version.

### Assertion

A proposed claim extracted or inferred from a source. Assertions are **not canonical by default**.

### Evidence / Provenance

Evidence connects an assertion to its supporting source and location. Provenance answers where the assertion came from and which source version supported it.

### Conflict

A representation of competing assertions that cannot all be accepted under the same interpretation. Conflicts remain visible until resolved; the LLM must not silently choose a winner.

### ReviewDecision

The decision that accepts, rejects, or defers an assertion/canonical change. Decisions are audit records associated with the relevant assertion/conflict and actor metadata supported by the implementation.

### CanonicalFact

An approved assertion that belongs to the project's source of truth. Canonical facts retain provenance and approval history and are versioned per `(book, subject, predicate)`.

### Confidence

A signal about extraction or inference quality. Confidence can prioritize review but **does not make an assertion canonical**.

## Canonical state lifecycle

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

The important boundary is between **proposed knowledge** and **approved knowledge**. Generation and validation may consume active canonical facts, but retrieval is never the source of truth.

## State ownership

- Author inputs are persisted as book state.
- Outline approval changes only through explicit application/API actions.
- Chapter drafts are generated by Writer/Corrector agents and persisted as immutable versions.
- Reviews are generated by the Reviewer or deterministic validation path and persisted per attempt.
- Accepted summaries are generated by the Summarizer and persisted on the chapter as continuity data.
- Canonical knowledge changes are explicit application actions backed by evidence and review decisions.
- Agents may extract, compare, classify, or propose knowledge changes, but do not own canonical state transitions.
- The workflow owns execution progress, not canonical domain truth.
- SQLite is an implementation detail of persistence.

## Retrieval rule

Lexical, semantic, hybrid, vector, full-text, or graph retrieval mechanisms may optimize access to canonical knowledge. They are **retrieval mechanisms, not canonical stores**. The authoritative state remains structured, persisted, provenance-aware, and reviewable.

## Evolution rule

If a persisted field or invariant changes, update this document in the same change and add an ADR when the change affects an architectural decision.
