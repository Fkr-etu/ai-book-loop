# ADR-0003: Workflow Orchestration

- Status: Accepted
- Date: 2026-09-01

## Context

Chapter generation contains a bounded sequence of writing, validation, review, retry, and summarization steps. The project initially considered LangGraph, but most business rules are deterministic and can be expressed directly in Python.

## Decision

Keep workflow orchestration isolated behind the chapter workflow component. Prefer plain Python for simple orchestration. Use LangGraph only when graph/state orchestration provides a concrete benefit; its APIs must not leak into domain or application boundaries.

## Consequences

- The MVP stays simpler and easier to test.
- LangGraph remains replaceable.
- Complex orchestration can be introduced later without coupling the domain to the framework.
- The workflow boundary must remain explicit as features are added.
