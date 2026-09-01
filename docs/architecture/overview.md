# Architecture Overview

## Layers

```text
CLI
 │
 ▼
Application use cases
 │
 ▼
Domain models + ports
 ▲
 │
Infrastructure adapters
 │
 ├── SQLite repository
 └── configurable LLM provider
```

Workflow orchestration is isolated from the domain. Agents encapsulate LLM-facing capabilities; use cases decide when those capabilities are invoked.

## Main responsibilities

### Domain

Owns book state and domain concepts such as books and chapters. It must remain independent of SQLite, Gemini, LangGraph, and the CLI.

### Application

Owns business actions such as creating a book, generating an outline, approving an outline, adding a chapter, and generating a chapter. It coordinates ports and domain state.

### Agents

Provide focused LLM capabilities such as outline generation, writing, review, and summarization. They should not become business orchestrators.

### Workflow

Coordinates the multi-step chapter generation loop. The workflow can use LangGraph where useful, but the rest of the application must not depend on that implementation choice.

### Infrastructure

Provides concrete persistence, configuration, and LLM provider implementations and assembles them in the composition root.

### CLI

Translates command-line input into application use-case calls and presents results. It contains no business rules or infrastructure wiring beyond obtaining the composition root.

## Composition root

`infrastructure/container.py` is the application composition root. It wires settings, repository, LLM provider, agents, workflow, and use cases. New entry points should reuse this assembly rather than constructing provider-specific dependencies themselves.
