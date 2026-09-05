# Canonical review workflow

This document describes the current evidence-backed Canon review behavior.

```text
Assertions
    ↓
Conflict detection
    ↓
Human/application review
    ├── reject → rejected assertion
    ├── defer  → deferred assertion
    └── accept → ReviewDecision → CanonicalFact
                         ↓
                    audit history
```

## Conflict semantics

The deterministic conflict detector currently flags assertions when they share the same normalized `subject` and `predicate` but have different normalized `object` values.

This is intentionally conservative: the engine represents a contradiction; it does not ask an LLM to decide which value is true.

## Review semantics

Every review creates a `ReviewDecision`. Decisions are append-only audit records.

- `reject` makes the assertion non-canonical.
- `defer` keeps the assertion available for later review.
- `accept` changes the assertion to `accepted` and creates a `CanonicalFact`.

When an assertion is accepted, competing proposed/deferred assertions are explicitly rejected with their own audit decisions, and the conflict is resolved in favor of the accepted assertion.

Canonical facts are versioned per `(book, subject, predicate)`. A new accepted value deactivates the previous active fact while preserving its historical version.

## Boundary

`CanonicalFact` is the source-of-truth representation produced by explicit review. Ingestion cannot create Canon directly, and LLM agents do not own Canon state transitions.

Active canonical facts can be consumed by generation/validation through the configured context/retrieval boundary. The provenance chain remains:

`CanonicalFact → ReviewDecision → Assertion → Evidence → SourceDocument`
