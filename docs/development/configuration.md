# Configuration

Runtime configuration is owned by infrastructure settings and consumed by the composition root.

## Rules

- Do not read environment variables directly from domain or use-case code.
- Provider-specific settings belong in infrastructure.
- Keep credentials out of source control.
- Tests should provide deterministic fake dependencies instead of production credentials.

## LLM provider

The production provider is Gemini, behind the application's LLM protocol. Provider-specific configuration stays in infrastructure so application behavior does not depend on Gemini-specific APIs.

The Critical Eye may use a dedicated model through `GRILL_LLM_MODEL`; when unset, it follows the main configured LLM model.

## Persistence

PostgreSQL is the application's persistence layer for production and the default local integration path. Database configuration is supplied through infrastructure settings rather than embedded in application logic.

Long-running analysis jobs are also persisted in PostgreSQL and claimed by a separate worker. See [`async-analysis-jobs.md`](../architecture/async-analysis-jobs.md) and ADR 0009 for the queue/lease design.

For exact variable names and defaults, consult the current settings implementation; this document intentionally avoids duplicating implementation details that can drift.
