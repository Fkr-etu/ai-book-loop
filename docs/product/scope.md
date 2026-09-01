# Scope

## In scope

- Create and persist a book.
- Capture theme, author idea, lore, and constraints.
- Generate an outline with a configurable LLM provider.
- Require explicit author approval of the outline.
- Create chapters sequentially.
- Generate one chapter at a time.
- Lint and review generated chapters.
- Retry rejected chapters within a bounded limit.
- Persist chapter versions and reviews.
- Produce a canonical chapter summary for continuity.
- Provide a minimal CLI.
- Provide a modern Web UI ("Manuscript Studio" in `web/`):
  - Author Dashboard & Multi-book Catalog (`/dashboard`)
  - Authentication views (`/login`, `/register`)
  - 3-step Project Setup Wizard (`/setup`)
  - Parchment Manuscript Writing Desk & AI Wing Assistant (`/studio`)
  - Outline & Narrative Structure Editor (`/studio/outline`)
  - Character Deep Editor with psychological traits & secrets (`/studio/characters`)
  - World Bible & Lore Codex (`/studio/lore`)
  - Interactive Lore Relationship Graph (`/studio/lore-graph`)
  - Creative Intention Lab & Linter Rule Manager (`/studio/intention-lab`)
  - Validation Loop & Critique Simulator (`/studio/validation-loop`)
  - Studio d'Exportation with Markdown, EPUB, PDF, DOCX formats (`/studio/export`)
  - Pricing & Subscriptions (`/pricing`)
- Persist data in SQLite (backend) and `localStorage` mock API (frontend).
- Run automated tests in CI (pytest & Playwright).

## Out of scope

- Production cloud multi-region deployment.
- Vector database long-term memory orchestration.
