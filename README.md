# AI Book Loop / Manuscript Studio

AI Book Loop is a **narrative consistency engine for creators who build complex, evolving universes**. The first product is an author-focused book-writing and review loop; screenwriters and Game Masters are adjacent creator segments to validate later.

> **Core promise:** Keep your universe coherent, even as it grows and changes.

> **Status:** Web UI (Manuscript Studio) and Python CLI under active development.

## Why Book Loop?

Generative AI can produce a convincing scene, chapter, NPC or plot idea. The difficult problem is keeping a long-lived universe coherent after many creations and revisions.

Book Loop keeps an approved Canon, checks new proposals against it, surfaces continuity and quality issues, and lets the creator decide what becomes canonical.

**Other tools help you create or store the universe. Book Loop helps you change it without silently breaking it.**

## Who it is for

- **Authors:** write with AI without losing the thread of the story.
- **Game Masters:** evolve a campaign without losing the memory of the world.
- **Screenwriters:** evolve scripts and story universes without breaking continuity.

The current MVP is deliberately focused on the **Book / author wedge**. Adjacent segments are product hypotheses, not separate products at launch.

## How it works

The creator moves through a controlled loop:

```text
Creator intent
     ↓
Context / existing Canon
     ↓
Outline / proposal
     ↓
Approval gate
     ↓
Draft / new content
     ↓
Validation + structured review
  ↙                    ↘
Correct / retry       Accept
     ↓                    ↓
Review again          Summary
                          ↓
                    Approved Canon
                          ↓
                 Next chapter / revision
```

Each chapter run has durable execution state and an idempotency identity. Generated versions remain immutable. Canonical knowledge is updated only through explicit application review decisions.

The creator remains the source of creative intent. LLMs propose and critique; application code controls approvals, sequencing, validation, persistence, recovery and retry limits.

## Project Architecture & Structure

- **Backend Core Engine (`book_loop/`):** layered/hexagonal Python architecture, chapter workflow orchestration, SQLite persistence, Canon support, and CLI interface.
- **Frontend Studio (`web/`):** Next.js App Router application ("Manuscript Studio") built with TypeScript, Tailwind CSS v4, React Flow (`@xyflow/react`), API service layer, and Playwright E2E testing suite.

## Quick start

### Python Backend & CLI

Install the project using the Python packaging workflow declared in `pyproject.toml`.

Inspect the CLI with:

```bash
python -m book_loop.cli.main --help
```

Run the backend tests with:

```bash
uv run --extra dev pytest
```

A Gemini API key is only required when using the real Gemini provider.

### Manuscript Studio Frontend (`web/`)

Start the Next.js development server:

```bash
cd web
npm install
npm run dev
```

Run the Playwright E2E suite locally with:

```bash
cd web
npm run test:e2e
```

## Architecture

The project uses a lightweight layered/hexagonal architecture:

```text
Web UI (Next.js) / CLI
      ↓
Application use cases + policies
      ↓
Domain + ports
      ↑
Infrastructure adapters
      ├── SQLite
      └── Configurable LLM provider
```

The chapter workflow is isolated from the rest of the application. `LangGraph` remains an implementation-compatible orchestration representation; the durable `ChapterWorkflow.run()` path uses a persisted Python state machine so execution can resume after a process restart.

## Documentation

### For contributors and AI agents

Start with [`AGENTS.md`](AGENTS.md). It contains the repository rules and points to the canonical documentation.

### Product

- [`docs/product/vision.md`](docs/product/vision.md) — product vision, narrative consistency category, Canon and creator expansion
- [`docs/product/positioning.md`](docs/product/positioning.md) — product positioning, personas, competition, differentiation and business-model hypothesis
- [`docs/product/strategy.md`](docs/product/strategy.md) — strategic choices, moat, and sequencing logic
- [`docs/product/scope.md`](docs/product/scope.md) — current MVP boundary
- [`docs/product/roadmap.md`](docs/product/roadmap.md) — product sequence, creator validation and expansion gates
- [`docs/product/pricing-strategy.md`](docs/product/pricing-strategy.md) — pricing and unit-economics hypotheses
- [`docs/product/infrastructure-costs.md`](docs/product/infrastructure-costs.md) — infrastructure planning scenarios

### Architecture

- [`docs/architecture/overview.md`](docs/architecture/overview.md) — current architecture
- [`docs/architecture/principles.md`](docs/architecture/principles.md) — architectural invariants
- [`docs/architecture/boundaries.md`](docs/architecture/boundaries.md) — dependency boundaries
- [`docs/architecture/workflows.md`](docs/architecture/workflows.md) — current book/chapter workflows and recovery semantics
- [`docs/architecture/data-model.md`](docs/architecture/data-model.md) — persisted domain and workflow-run model
- [`docs/architecture/chapter-workflow-recovery.md`](docs/architecture/chapter-workflow-recovery.md) — durable checkpoints, idempotency and known limitations
- [`docs/architecture/canonical-review.md`](docs/architecture/canonical-review.md) — current Canon review semantics
- [`docs/architecture/document-ingestion.md`](docs/architecture/document-ingestion.md) — document-ingestion design
- [`docs/architecture/decisions/`](docs/architecture/decisions/) — historical architecture decisions

### Development

- [`docs/development/setup.md`](docs/development/setup.md) — local setup
- [`docs/development/testing.md`](docs/development/testing.md) — testing strategy
- [`docs/development/configuration.md`](docs/development/configuration.md) — configuration rules
- [`docs/development/contributing.md`](docs/development/contributing.md) — contribution workflow
- [`docs/glossary.md`](docs/glossary.md) — project terminology

## Development principles

1. Business actions belong in explicit use cases.
2. Deterministic rules stay in Python.
3. LLM providers are replaceable infrastructure.
4. Creator intent and canonical continuity are first-class concerns.
5. Preserve generated history rather than silently overwriting it.
6. Avoid unnecessary LLM calls and bound retries.
7. Tests must run without external LLM services.
8. Architecture and documentation evolve together.

See `AGENTS.md` and the documentation index for the complete rules.
