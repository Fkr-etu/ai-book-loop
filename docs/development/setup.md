# Development Setup

## Prerequisites

- Python 3.12+ for backend.
- Node.js 20+ and npm for frontend.
- Git.
- A Gemini API key only when exercising the real backend LLM provider.

## Install

### Backend (Python)

Install dependencies using `uv`:

```bash
uv sync --extra dev
```

### Frontend (Next.js / Manuscript Studio)

Navigate to `web/` and install dependencies:

```bash
cd web
npm install
npx playwright install chromium
```

## Run Applications

### CLI

`python -m book_loop.cli.main --help`

### Web Studio

```bash
cd web
npm run dev
```

Open `http://localhost:3000` in your browser.
