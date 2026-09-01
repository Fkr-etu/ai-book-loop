# ADR-0002: Configurable LLM Provider

- Status: Accepted
- Date: 2026-09-01

## Context

The MVP will use Gemini, while application logic should remain portable and tests must not require a live provider.

## Decision

Expose LLM capabilities through an application-facing port and provide Gemini as a configurable infrastructure implementation. Provider configuration belongs in infrastructure settings/composition.

## Consequences

- Gemini can be replaced without changing domain rules or use-case intent.
- Tests can use deterministic fakes.
- Provider-specific configuration and SDK details remain isolated.
- The project can optimize provider usage and cost centrally.
