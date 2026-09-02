# Generation → Review → Correction

Stage 9 makes chapter generation an explicit bounded feedback loop.

```text
START
  ↓
Writer → persist version N
  ↓
Linter / Reviewer → persist review N
  ↓
accept? ───────────────→ Summarizer → APPROVED
  │
  └─ retry → Corrector → persist version N+1 → Reviewer
                 │
                 └──────── bounded by max_retries

max retries reached → NEEDS_REVIEW decision / no summary
```

## Responsibilities

- `WriterAgent` creates the first draft.
- `ChapterLinter` performs deterministic inexpensive checks before an LLM review.
- `ReviewerAgent` evaluates a valid draft and returns structured `SceneReview` feedback.
- `CorrectorAgent` receives the current draft plus the review issues/suggestions and produces the next version.
- `ChapterWorkflow` owns iteration, persistence and the review policy.
- `BookRepository` persists every draft version and every review for traceability.

`max_retries` is the maximum number of generated versions/review cycles, including the initial draft. The workflow therefore cannot loop indefinitely.

## Persistence and status

Every generated version is persisted before review. Every review is persisted, including deterministic lint failures. A chapter is marked `APPROVED` only after an accepted review and successful summarization.

An unsuccessful run returns the `needs_review` decision without summarizing or promoting the chapter. Manual intervention can then inspect the persisted versions and reviews.

## Canon boundary

This loop reads context, including relevant Canonical Knowledge through `ContextBuilder`, but it never creates, updates, resolves or promotes Canonical Facts. Canon remains governed by the ingestion/conflict-review workflow.
