# Testing

## Principles

Tests should validate behavior at the appropriate boundary and remain deterministic.

## LLM tests

Do not call Gemini or another live provider from the normal test suite. Use deterministic fakes for application and workflow tests.

## What to test

- Domain invariants and state transitions.
- Use cases with fake repositories/providers.
- Workflow behavior, including review decisions, retries, and summaries.
- Repository persistence against an isolated SQLite database.
- CLI parsing and command behavior without requiring external services.

## CI

The GitHub Actions test pipeline is the required gate before merging. A local passing test run is useful, but a failing CI pipeline means the change is not complete.

## Regression discipline

When a CI failure reveals a bug, fix the underlying behavior or test contract rather than weakening the assertion solely to make the pipeline green.
