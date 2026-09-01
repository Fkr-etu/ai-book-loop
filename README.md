# AI Book Loop

AI Book Loop assists an author in producing a coherent book chapter by chapter while preserving author intent and canonical continuity.

> **Status:** MVP under active development.

## How it works

The author provides a theme, inspiration or lore, an idea, and optional constraints. The system generates an outline, waits for explicit author approval, then generates chapters one at a time while reviewing and preserving canonical context.

```text
Author intent
     |
     v
  Outline -----> Author approval
                     |
                     v
              Chapter generation
                     |
                Review / retry
                     |
                     v
              Canonical summary
                     |
                     v
                Next chapter
```

## MVP

- Minimal CLI
- SQLite persistence
- Configurable LLM provider (Gemini initially)
- Outline generation and explicit approval
- Sequential chapter generation
- Review and bounded retry loop
- Canonical summaries for continuity
- Automated tests in GitHub Actions

## Quick start

The project uses Python and the development dependencies declared in `pyproject.toml`.

```bash
python -m book_loop.cli.main --help
```

Run the test suite with the project's configured pytest command. The normal test suite does not require a live LLM provider.

## Documentation

- **AI agents:** [`AGENTS.md`](AGENTS.md) — rules and workflow for modifying the repository.
- **Product:** [`docs/product/`](docs/product/) — vision, goals, and MVP scope.
- **Architecture:** [`docs/architecture/`](docs/architecture/) — current design, boundaries, workflows, data model, and ADRs.
- **Development:** [`docs/development/`](docs/development/) — setup, testing, configuration, and contribution workflow.
- **Glossary:** [`docs/glossary.md`](docs/glossary.md) — project terminology.

## Architecture at a glance

```text
CLI
 |
 v
Application use cases
 |
 v
Domain + ports
 ^
 |
Infrastructure adapters
 |--- SQLite
 `--- LLM provider (Gemini)
```

Business rules belong in Python and application/domain layers. Provider-specific details stay behind ports and infrastructure adapters. See [`docs/architecture/principles.md`](docs/architecture/principles.md) for the full rules.

## Development workflow

1. Start from an up-to-date `main` branch.
2. Read `AGENTS.md` and the relevant documentation.
3. Make a focused change with tests.
4. Update documentation when behavior or architecture changes.
5. Run the test suite and wait for CI to pass.
6. Commit and push the focused change.

See [`docs/development/contributing.md`](docs/development/contributing.md) for details.
