# AI Book Loop / Manuscript Studio

AI Book Loop assists an author in producing a coherent book chapter by chapter while preserving author intent and canonical continuity.

> **Status:** Web UI (Manuscript Studio) and Python CLI MVP active.

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

## Project Structure

- **Backend / Core Engine (`book_loop/`):** Python layered architecture, LangGraph workflow orchestration, SQLite persistence, and CLI.
- **Frontend Studio (`web/`):** Next.js App Router application ("Manuscript Studio") built with TypeScript, Tailwind CSS v4, React Flow (`@xyflow/react`), mock API service layer (`web/src/services/api.ts`), and Playwright E2E testing suite.

## Quick start

### Python Backend & CLI

Install the project using the Python packaging workflow declared in `pyproject.toml`.

Inspect the CLI with:

```bash
python -m book_loop.cli.main --help
```

Run Python tests:

```bash
uv run --extra dev pytest
```

### Manuscript Studio Frontend (`web/`)

Start the Next.js development server:

```bash
cd web
npm install
npm run dev
```

Run Playwright E2E tests:

```bash
cd web
npm run test:e2e
```

## Architecture

The project uses a lightweight layered/hexagonal architecture:

```text
Web UI (Next.js) / CLI
      ↓
Application use cases / Service Layer
      ↓
Domain + ports
      ↑
Infrastructure adapters
      ├── SQLite / localStorage
      └── LLM provider / Mock API
```

`book_loop.infrastructure.container` is the Python composition root. `web/src/services/api.ts` provides the frontend mock API service layer decoupled from React context UI state.

## Documentation

### Product

- [`docs/product/vision.md`](docs/product/vision.md) — product mission and principles
- [`docs/product/scope.md`](docs/product/scope.md) — product scope & features

### Architecture

- [`docs/architecture/overview.md`](docs/architecture/overview.md) — current architecture
- [`docs/architecture/principles.md`](docs/architecture/principles.md) — architectural invariants
- [`docs/architecture/boundaries.md`](docs/architecture/boundaries.md) — dependency boundaries
- [`docs/architecture/workflows.md`](docs/architecture/workflows.md) — book and chapter workflows
- [`docs/architecture/data-model.md`](docs/architecture/data-model.md) — persisted domain concepts
- [`docs/architecture/decisions/`](docs/architecture/decisions/) — ADRs and architectural decisions

### Development

- [`docs/development/setup.md`](docs/development/setup.md) — development setup
- [`docs/development/testing.md`](docs/development/testing.md) — testing strategy
- [`docs/development/configuration.md`](docs/development/configuration.md) — runtime configuration
- [`docs/development/contributing.md`](docs/development/contributing.md) — contribution workflow
- [`docs/glossary.md`](docs/glossary.md) — project terminology
