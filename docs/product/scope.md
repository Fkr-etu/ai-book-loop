# MVP Scope

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
- Persist data in SQLite.
- Run automated tests in CI.

## Explicitly out of scope for the MVP

- Web UI.
- Authentication and multi-user collaboration.
- Production deployment infrastructure.
- Advanced long-term memory/vector databases.
- Provider-specific application logic.
- Complex agent orchestration where plain Python is sufficient.
