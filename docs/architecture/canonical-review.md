# Canonical review workflow

This document describes the current evidence-backed Canon review behavior. Canon is explicit application state: extraction, detection and retrieval may propose or report information, but only review can promote an assertion to an active `CanonicalFact`.

```text
Approved source
      ↓
Assertion + Evidence
      ↓
Conflict / consistency detection
      ↓
Human/application review
      ├── reject → rejected assertion
      ├── defer  → deferred assertion
      └── accept → ReviewDecision → CanonicalFact
                         ↓
                    audit history
```

## Conflict and consistency semantics

The deterministic assertion conflict detector currently flags assertions when they share the same normalized `subject` and `predicate` but have different normalized `object` values. This is an evidence-backed representation of competing claims; it is not a truth decision.

The author-facing consistency layer exposes these and other detector results through the shared `ConsistencyIssue` contract. It may also consume diagnostics produced when newly supplied text is compared with active Canon facts. Those diagnostics are signals for the author, not automatic Canon mutations.

Detection is intentionally conservative: the engine does not ask an LLM to decide which value is true and does not silently resolve a conflict.

## Review semantics

Every review creates a `ReviewDecision`. Decisions are append-only audit records.

- `reject` makes the assertion non-canonical.
- `defer` keeps the assertion available for later review.
- `accept` changes the assertion to `accepted` and creates a `CanonicalFact`.

When an assertion is accepted, competing proposed/deferred assertions are explicitly rejected with their own audit decisions, and the conflict is resolved in favor of the accepted assertion.

Canonical facts are versioned per `(book, subject, predicate)`. A new accepted value deactivates the previous active fact while preserving its historical version.

## Provenance

The reviewable provenance chain is:

`CanonicalFact → ReviewDecision → Assertion → Evidence → SourceDocument`

A `ConsistencyIssue` can retain assertion identifiers and evidence excerpts so the author can inspect why it was raised. Confidence can prioritize review but never makes an assertion canonical.

## Boundary

`CanonicalFact` is the source-of-truth representation produced by explicit review. Ingestion cannot create Canon directly, consistency detection cannot approve it, retrieval cannot mutate it, and LLM agents do not own Canon state transitions.

Active canonical facts can be consumed by generation/validation through the configured context/retrieval boundary. The retrieval layer is read-only with respect to Canon.
