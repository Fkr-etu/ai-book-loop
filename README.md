# AI Book Loop

AI Book Loop assists an author in producing a coherent book chapter by chapter while preserving author intent and canonical continuity.

> **Status:** MVP under active development.

## How it works

The author provides a theme, inspiration or lore, an idea, and optional constraints. The system then works incrementally:

```text
Author intent
     ↓
  Outline
     ↓
Approval gate
     ↓
 Chapter
     ↓
Lint / Review
  ↙       ↘
Retry    Accept
             ↓
     Canonical summary
             ↓
       Next chapter
```

The author remains the source of creative intent. Generated content is proposed by the LLM, while application code controls approvals, sequencing, validation, and retry limits.

## MVP

- Minimal CLI
- SQLite persistence
- Configurable LLM provider, with Gemini as the initial provider
- Author theme, idea, lore, and constraints
- Outline generation and explicit approval
- Sequential, chapter-scoped generation
- Linting, review, and bounded retry
- Chapter history and canonical summaries
- Automated tests and GitHub Actions CI

Out of scope for the MVP: web UI, authentication/multi-user collaboration, production deployment infrastructure, vector databases, and unnecessary framework-heavy orchestration.

## Quick start

Install the project using the Python packaging workflow declared in `pyproject.toml`.

Inspect the CLI with:

```bash
python -m book_loop.cli.main --help
```

The normal test suite does not require a live LLM provider:

```bash
pytest
```

A Gemini API key is only required when using the real Gemini provider.

## Architecture

The project uses a lightweight layered/hexagonal architecture:

```text
CLI / adapters
      ↓
Application use cases
      ↓
Domain + ports
      ↑
Infrastructure adapters
      ├── SQLite
      └── LLM provider
```

`book_loop.infrastructure.container` is the composition root. It wires infrastructure implementations, agents, workflow, and application use cases. Provider-specific details must not leak into the domain or use cases.

The chapter workflow is isolated from the rest of the application. Plain Python is preferred when sufficient; LangGraph is an implementation detail rather than an application dependency.

## Documentation

### For contributors and AI agents

Start with [`AGENTS.md`](AGENTS.md). It contains the rules that must be followed when modifying the repository.

### Product

- [`docs/product/vision.md`](docs/product/vision.md) — product mission and principles
- [`docs/product/scope.md`](docs/product/scope.md) — MVP scope and explicit non-goals

### Architecture

- [`docs/architecture/overview.md`](docs/architecture/overview.md) — current architecture
- [`docs/architecture/principles.md`](docs/architecture/principles.md) — architectural invariants
- [`docs/architecture/boundaries.md`](docs/architecture/boundaries.md) — dependency boundaries
- [`docs/architecture/workflows.md`](docs/architecture/workflows.md) — book and chapter workflows
- [`docs/architecture/data-model.md`](docs/architecture/data-model.md) — persisted domain concepts
- [`docs/architecture/decisions/`](docs/architecture/decisions/) — ADRs and architectural history

### Development

- [`docs/development/setup.md`](docs/development/setup.md) — development setup
- [`docs/development/testing.md`](docs/development/testing.md) — testing strategy
- [`docs/development/configuration.md`](docs/development/configuration.md) — runtime configuration
- [`docs/development/contributing.md`](docs/development/contributing.md) — contribution workflow
- [`docs/glossary.md`](docs/glossary.md) — project terminology

## Development principles

1. Business actions belong in explicit use cases.
2. Deterministic rules stay in Python.
3. LLM providers are replaceable infrastructure.
4. Author intent and canonical continuity are first-class concerns.
5. Preserve generated history rather than silently overwriting it.
6. Avoid unnecessary LLM calls and bound retries.
7. Tests must run without external LLM services.
8. Architecture and documentation evolve together.

See `AGENTS.md` and the architecture documentation for the complete rules.
