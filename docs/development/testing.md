# Testing

## Principles

Tests should validate behavior at the appropriate boundary and remain deterministic.

## What to test

- **Python Backend Unit Tests (`tests/`):**
  - Domain invariants and state transitions.
  - Use cases with fake repositories/providers.
  - Workflow behavior, including review decisions, retries, and summaries.
  - Run with: `uv run --extra dev pytest`

- **Frontend E2E Tests (`web/tests/`):**
  - Page rendering across all 13 routes.
  - Form interactions, character creation, lore additions, setup wizard steps, and Linter validation.
  - Visual verification and automated screenshot captures.
  - Run with: `cd web && npm run test:e2e`

## CI

Automated tests execute in CI pipelines to ensure no regressions are introduced.
