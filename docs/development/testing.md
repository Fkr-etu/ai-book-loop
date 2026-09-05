# Testing

## Principles

Tests should validate behavior at the appropriate boundary and remain deterministic.

## LLM tests

Do not call Gemini or another live provider from the normal test suite. Use deterministic fakes for application and workflow tests.

## What to test

- **Python Backend Unit Tests (`tests/`):**
  - Domain invariants and state transitions.
  - Use cases with fake repositories/providers.
  - Workflow behavior, including linting, linguistic validation, review decisions, retries, correction, summaries and terminal `needs_review` outcomes.
  - Workflow idempotency and restart/recovery semantics.
  - Repository persistence against an isolated SQLite database.
  - Canon extraction, conflict detection and explicit review-to-Canon transitions.
  - CLI parsing and command behavior without requiring external services.
  - Run with: `uv run --extra dev pytest`

- **Frontend E2E Tests (`web/tests/`):**
  - Page rendering across the currently implemented routes.
  - Form interactions, character creation, lore additions, setup wizard steps, and Linter validation.
  - Visual verification and automated screenshot captures.
  - Run with: `cd web && npm run test:e2e`

## Workflow recovery test matrix

At minimum, chapter workflow tests should cover:

1. **Normal accept** — version persisted, review persisted, summary persisted and chapter approved.
2. **Retry/correction** — each correction creates a new immutable version and clears the previous review decision before re-review.
3. **Retry exhaustion** — the run becomes `needs_review` without an accepted summary.
4. **Duplicate request** — the same idempotency key does not call agents twice after completion.
5. **Crash after version persistence** — a new workflow instance reuses the persisted version rather than invoking Writer again.
6. **Crash during a later step** — the run resumes from its last committed checkpoint.
7. **Explicit idempotency key** — repeated calls with the same key address the same workflow run.
8. **New generation** — once the accepted `current_version` advances, the default key changes so a deliberate later generation can create a new run/version.

The recovery tests should use a real isolated SQLite workflow store when validating persistence across workflow instances. In-memory stores are appropriate for focused unit tests.

## Known recovery limitation

The current workflow persists review data and workflow-run checkpoints as separate writes. A process crash between those writes can cause the Reviewer to be called again on resume. This is a known reliability gap and should be closed by an atomic transaction or a durable review lookup/idempotency constraint before stronger exactly-once expectations are made.

Cross-process duplicate execution is also not fully prevented. Same-process execution is serialized by a per-run lock; distributed workers require a persistent lease/claim protocol.

## CI

The GitHub Actions test pipeline is the required gate before merging. A local passing test run is useful, but a failing CI pipeline means the change is not complete.

CI currently runs the Python test suite. Frontend build/lint/E2E checks remain local development checks until they are explicitly added to the CI workflow.

## Regression discipline

When a CI failure reveals a bug, fix the underlying behavior or test contract rather than weakening the assertion solely to make the pipeline green.
