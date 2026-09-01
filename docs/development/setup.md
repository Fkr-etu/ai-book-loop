# Development Setup

## Prerequisites

- Python version required by the project's packaging configuration (3.12+).
- Node.js 20+ and npm for frontend development.
- Git.
- A Gemini API key only when exercising the real backend provider.

## Install

### Python Backend

Use the project's declared Python packaging/development workflow from `pyproject.toml`.

```bash
uv sync --extra dev
```

The normal test suite does not require a Gemini key.

### Frontend (Manuscript Studio)

Navigate to `web/` and install dependencies:

```bash
cd web
npm install
npx playwright install chromium
```

## Run tests

Run the Python backend test suite with the project's configured pytest command:

```bash
uv run --extra dev pytest
```

Run the Playwright E2E frontend test suite:

```bash
cd web
npm run test:e2e
```

CI executes the same test suites as the merge gate.

## CLI & Web Studio

### CLI

The CLI is the primary MVP CLI entry point. Use `python -m book_loop.cli.main --help` to inspect the commands supported by the current implementation.

### Web Studio

Start the Next.js development server:

```bash
cd web
npm run dev
```

Open `http://localhost:3000` in your browser.

## Configuration

Runtime configuration is handled by `book_loop.infrastructure.config.Settings` and assembled by the composition root. Do not add provider or database configuration directly to CLI/use-case code.
