# Generation → Review → Correction

Chapter generation is an explicit bounded feedback loop. The workflow owns execution, persistence and retry policy; Canon and corpus consistency remain separate author-controlled boundaries.

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

## Canon and consistency boundaries

Generation reads context, including relevant active `CanonicalFact` records through `ContextBuilder`, but it does not own Canon state transitions.

After an approved chapter version is persisted, assertion extraction can contribute proposed knowledge to the corpus. Consistency/conflict detection may report contradictions, while explicit review remains responsible for Canon promotion or resolution.

The generation loop therefore follows this boundary:

```text
Canonical knowledge ──read──→ generation context
                                ↓
                           Writer / Corrector
                                ↓
                         approved chapter
                                ↓
                    proposed assertions/evidence
                                ↓
                     consistency detection
                                ↓
                          human review
                                ↓
                         CanonicalFact
```

Generation must not bypass that review path by directly creating, updating, resolving or promoting Canonical Facts.
