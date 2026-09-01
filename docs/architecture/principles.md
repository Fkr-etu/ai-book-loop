# Architecture Principles

These principles are the constraints used when evolving the codebase.

## 1. Explicit use cases

A meaningful business action is represented by an application use case. Use cases orchestrate domain operations and ports; they do not contain provider-specific implementation details.

## 2. Dependency direction

The intended direction is:

`CLI / infrastructure adapters -> application use cases -> domain / ports <- infrastructure implementations`

Infrastructure implements ports; domain code never imports infrastructure.

## 3. Author intent is authoritative

Theme, inspiration, lore, author ideas, constraints, and explicit approvals are product data, not incidental prompt text. Generation and review must preserve these inputs.

## 4. Canonical continuity

A generated chapter is not the sole source of future context. Approved/canonical information is persisted and used to construct context for subsequent chapters.

## 5. Deterministic rules stay deterministic

Validation, sequencing, retry limits, state transitions, and other rules that can be expressed reliably in Python must not be delegated to an LLM.

## 6. LLMs are replaceable infrastructure

Application code depends on an LLM capability/port. Gemini is a configurable implementation, not a domain dependency.

## 7. Orchestration should be as simple as possible

Use plain Python for orchestration when it is sufficient. LangGraph is allowed only where graph/state orchestration provides real value and should remain isolated from the rest of the application.

## 8. Preserve history

Drafts, reviews, and canonical summaries are part of the book's evolution. New generation attempts should not destroy useful previous state.

## 9. Cost is a design constraint

Avoid unnecessary model calls. Perform deterministic checks first, keep context focused, persist reusable information, and bound retries.

## 10. Test without external services

Core tests must not require a live LLM or network. Provider fakes should exercise application behavior deterministically.

## 11. Documentation follows code

When a change alters a documented behavior, boundary, workflow, or architectural decision, update the relevant documentation in the same change. Significant decisions get an ADR.
