# Data Model

This document describes the conceptual persisted state. The implementation remains the source of truth for exact serialization details.

## Book

A book contains the author's creative inputs and the generated state needed to continue writing.

Core inputs:

- `id`
- `title`
- `theme`
- `author_idea`
- `lore`
- `constraints`

Generated/approval state includes the outline, its approval status, and chapters.

## Chapter

A chapter is identified within a book by its sequence number and contains at least a title and objective. Generation adds draft/review/summary state as defined by the current workflow implementation.

## Canonical context

Canonical context is derived from approved book information and accepted chapter summaries. It exists to provide continuity without requiring the system to resend or regenerate the entire history on every LLM call.

## State ownership

- Author inputs are persisted as book state.
- Approval flags are application state and are changed by explicit use cases.
- Generated content is produced by agents/workflows and persisted through repository ports.
- SQLite is an implementation detail of persistence.

## Evolution rule

If a persisted field or invariant changes, update this document in the same change and add an ADR when the change affects an architectural decision.
