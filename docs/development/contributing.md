# Contributing

## Development loop

1. Start from an up-to-date `main` branch.
2. Create a focused feature or fix branch.
3. Read `AGENTS.md` and the documentation relevant to the change.
4. Make the smallest coherent change that preserves the architecture.
5. Add or update tests.
6. Update documentation in the same change when behavior or architecture changes.
7. Run the test suite.
8. Commit with a focused message.
9. Push the branch and open a pull request.

## Architectural changes

If a change alters a significant technology or boundary decision, add an ADR. Keep historical ADRs immutable and mark newer decisions as superseding older ones.

## Pull requests

PRs should explain the intent, the architectural impact, and how the change was validated. Do not merge with a failing test pipeline.
