# Workflows

## Book lifecycle

```text
CreateBook
  -> GenerateOutline
  -> author approves outline
  -> AddChapter (sequentially)
  -> GenerateChapter
  -> review / validation
  -> canonical summary
  -> next chapter
```

The application owns state transitions and approval rules. The LLM proposes content; it does not decide whether an author approval has happened.

## Chapter generation loop

A generation run is scoped to one chapter. The workflow receives the persisted book state and chapter number, builds bounded context, and coordinates the Writer → validation → Reviewer → Retry/Summary loop.

Current implementation is `ChapterWorkflow`, orchestrated with LangGraph. LangGraph is an orchestration adapter: domain models, ports and application rules must remain usable without importing LangGraph APIs.

```text
                    persisted BookState
                           |
                           v
                 ContextBuilder.for_chapter()
                           |
                           v
                         Writer
                           |
                           v
                    draft / candidate
                           |
                           v
                 deterministic ChapterLinter
                           |
                  +--------+--------+
                  |                 |
                invalid           valid
                  |                 |
                  v                 v
              retry/end          Reviewer
                                    |
                              ReviewDecision
                           +--------+--------+
                           |        |         |
                         retry    accept   needs_review
                           |        |         |
                           |        v         v
                           |     Summarizer   END
                           |        |
                           +--------+
                                    |
                                    v
                             persisted summary
                                    |
                                    v
                             chapter approved
```

### 1. Context construction

`ContextBuilder` creates the prompt context from persisted canonical/book state. For the current chapter it includes:

- author's original idea;
- theme;
- lore;
- the complete structured outline when available;
- global constraints;
- summaries of previous chapters only;
- the current chapter objective.

Rejected drafts are not used as canonical continuity context. Accepted chapter summaries are the continuity mechanism for subsequent chapters.

### 2. Writing

`WriterAgent` receives the built context and proposes the chapter draft. Each generated attempt is persisted through `save_chapter_version(book_id, chapter_number, attempt, draft)` before review.

The attempt number starts at `1` for the first generated draft and increments for every retry.

### 3. Deterministic validation

`ChapterLinter` runs before the LLM reviewer. A lint failure is treated as a retryable failure while the retry budget remains; after the budget is exhausted the workflow ends in `needs_review` rather than looping indefinitely.

This layer is intentionally deterministic and is not delegated to the LLM.

### 4. LLM review and decision policy

For a lint-valid draft, `ReviewerAgent` evaluates the draft against the chapter context. The review is persisted with the corresponding attempt.

`application.policies.review.decide()` converts the review result into one of three workflow decisions:

- `accept` — the draft meets the configured review threshold;
- `retry` — the draft is rejected and attempts remain;
- `needs_review` — the retry budget is exhausted and the workflow stops for human/application handling.

The configured `review_threshold` and `max_retries` are application policy, not model output.

### 5. Retry

A retry returns to `WriterAgent` with the same chapter context and creates a new persisted version. Retries are bounded by `max_retries`; there is no unbounded model-call loop.

The persisted attempt/review history is retained so a failed generation remains observable rather than silently replacing previous drafts.

### 6. Summary and canonicalization

When the review decision is `accept`, `SummarizerAgent` produces the chapter summary. The workflow then updates the persisted chapter with:

- `status = approved`;
- `current_version = accepted attempt`;
- `summary = generated summary`.

That summary becomes canonical continuity data for later chapters.

The current implementation therefore treats a reviewed-and-accepted draft as the source from which continuity is summarized; the summary, not the rejected attempts, is what is carried forward by `ContextBuilder`.

## Author approval gates

The outline must be explicitly approved before a chapter can be generated. This is a deterministic application rule and must remain outside the LLM.

The chapter-generation workflow refuses to run when `outline_approved` is false.

## Sequential chapter progression

Chapter generation is intentionally scoped to a single chapter. The application is responsible for adding chapters in sequence and for validating the outline before generation. The loop itself does not decide which chapter comes next.

## Failure and observability

A generation run can terminate in two ways without producing a canonical summary:

1. deterministic lint failures exhaust the retry budget;
2. the LLM reviewer rejects the draft until the retry budget is exhausted.

In both cases the workflow stops instead of silently approving content. Persisted chapter versions and reviews provide the audit trail available to the current repository implementation.

## Architecture boundary

Agents encapsulate LLM-facing capabilities; they do not own business orchestration. Application services/policies own context construction and review decisions. The workflow coordinates these capabilities.

LangGraph currently implements the state-machine execution, but it must remain replaceable. The domain and application layers must not depend on LangGraph-specific state or APIs.
