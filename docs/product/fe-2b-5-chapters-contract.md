# FE-2B.5 — Chapters contract

## Goal

Provide a persisted Chapters workspace for the author: select a chapter, inspect its persisted versions, generate a proposal, request a review, and make an author decision.

## Authority

The backend remains authoritative for `BookState`, chapter status, version numbers, version content, review results, and approval/rejection transitions.

The frontend may hold transient editor text and selection state, but must not invent chapter status, version numbers, review scores, or canonical state.

## Actions

- Generate: `generateChapter(chapterNumber)`.
- Review: `reviewChapter(chapterNumber, versionNumber, draftText)`.
- Approve: `approveChapter(chapterNumber)` only when the persisted chapter state allows a decision.
- Reject: `rejectChapter(chapterNumber)` only when the persisted chapter state allows a decision.

After a mutation, the UI must render the state returned by the API/store rather than guessing the next state.

## Mock mode

Deterministic mock behavior may remain available for local/CI E2E through the existing mock API configuration. It must not be presented as production data when the real API is enabled.

## Out of scope

No workflow engine changes, LLM prompt changes, Canon model changes, billing, analytics beyond the existing allowlist, or new persistence model are part of FE-2B.5.
