# ADR-0001: Application Architecture

- Status: Accepted
- Date: 2026-09-01

## Context

The project needs to evolve from a small CLI prototype into a maintainable book-generation application. Business rules must remain testable and independent from SQLite, Gemini, and orchestration frameworks.

## Decision

Use a lightweight layered/hexagonal architecture with explicit application use cases, domain models, and ports. Concrete persistence and LLM providers remain infrastructure adapters. The CLI uses the composition root and application use cases rather than implementing business logic.

## Consequences

- Business actions have explicit entry points.
- Infrastructure can be replaced without changing domain rules.
- Tests can use fakes instead of live providers.
- There is some additional structure compared with a direct script, but it protects the project's intended growth.

## Rejected alternatives

A direct CLI-to-LLM/SQLite architecture was rejected because it would couple the entry point to infrastructure and make future interfaces and provider changes expensive.
