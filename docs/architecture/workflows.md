# Workflows

## Book lifecycle

```text
CreateBook
  -> GenerateOutline
  -> author approves outline
  -> AddChapter (sequentially)
  -> GenerateChapter
  -> review / validation
  -> accepted summary
  -> next chapter
```

The application owns state transitions and approval rules. The LLM proposes content; it does not decide whether an author approval has happened.

## Chapter generation loop

A generation run is scoped to one chapter. The workflow receives persisted book state and chapter number, builds bounded context, and coordinates the Writer → deterministic validation → Reviewer → Retry/Summary loop.

`ChapterWorkflow.run()` is the production execution path. It uses a durable workflow-run checkpoint store and a small persisted state machine. `build()` remains available as a LangGraph-compatible representation, but it is not the mechanism used by `run()` to provide restartability.

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
                    persisted version
                           |
                           v
          deterministic lint + linguistic validation
                           |
                    +------+------+
                    |             |
                  blocking      valid
                    |             |
                    v             v
               retry/review    Reviewer
                                  |
                            ReviewDecision
                         +----------+----------+
                         |          |           |
                       retry      accept    needs_review
                         |          |           |
                         v          v           v
                      Correct    Summarizer     END
                         |          |
                         +-----> REVIEW
                                    |
                                    v
                             chapter approved
```

Each meaningful state transition is checkpointed. A workflow run is identified by `(book_id, chapter_number, idempotency_key)`.

### 1. Context construction

`ContextBuilder` creates prompt context from persisted book state and approved Canon context when configured. For the current chapter it includes:

- author's original idea;
- theme;
- lore;
- the complete structured outline when available;
- global constraints;
- summaries of previous chapters only;
- the current chapter objective;
- relevant active Canon facts when available.

Rejected drafts are not used as canonical continuity context. Accepted chapter summaries and active Canon facts are the continuity mechanisms for subsequent chapters.

### 2. Writing

The workflow reserves the next attempt number and checkpoints it **before** invoking the Writer. `WriterAgent` then proposes the chapter draft.

The generated attempt is persisted before review. If the process crashes after the version is persisted but before the next workflow checkpoint, recovery sees the existing version and reuses it instead of calling the Writer again.

The first attempt is version `1`; each retry/correction creates the next available persisted version.

### 3. Deterministic validation

`ChapterLinter` runs before the LLM reviewer. Linguistic validation also runs before the reviewer when configured.

- Blocking linguistic `ERROR` diagnostics prevent the LLM reviewer from being called.
- Non-blocking diagnostics are passed to the reviewer as structured input.
- Canon diagnostics are not sent through the linguistic contextualizer.
- Lint/validation failures follow the application's bounded retry policy.

This layer is intentionally deterministic wherever possible and is not delegated to the LLM.

### 4. Native structured LLM output

The Gemini adapter exposes:

- `generate()` for free-form text generation;
- `generate_structured()` for typed responses constrained by a JSON Schema derived from a Pydantic model.

Structured reviewer/extractor results are validated by the provider boundary and again by Pydantic before entering application logic. Prompt-only JSON conventions and ad-hoc regex repair are not the primary mechanism.

### 5. LLM review and decision policy

For a validation-clean draft, `ReviewerAgent` requests a native structured `SceneReview`. The reviewer evaluates author-intent fidelity, continuity, coherence and writing quality. It cannot directly mutate the book or Canon.

`application.policies.review.decide()` converts the review into:

- `accept` — the draft meets the configured review threshold;
- `retry` — the draft is rejected and attempts remain;
- `needs_review` — the retry budget is exhausted and the workflow stops for human/application handling.

The configured `review_threshold` and `max_retries` are application policy, not model output.

### 6. Structured assertion extraction

Canon extraction uses native structured output. `LLMAssertionExtractor` requests an `ExtractedAssertions` wrapper containing `ExtractedAssertion` items.

The adapter validates assertion offsets against the source chunk after schema validation. Extractors can propose assertions and evidence locations, but cannot promote anything into `CanonicalFact`. Human/application review remains authoritative.

### 7. Retry and correction

A retry moves the run to `correct`. `CorrectorAgent` receives the current draft and persisted review, and the resulting corrected draft is stored as a new immutable chapter version.

The review/decision fields are cleared before returning to `review`, preventing a previous decision from being reused for the corrected version.

Retries are bounded by `max_retries`; there is no unbounded model-call loop.

### 8. Summary and chapter approval

When the review decision is `accept`, `SummarizerAgent` produces the chapter summary. The workflow then persists:

- `status = approved`;
- `current_version = accepted attempt`;
- `summary = generated summary`.

The accepted summary becomes continuity data for later chapters. Rejected attempts remain in history but do not become canonical continuity memory.

### 9. Restart and idempotency

`GenerateChapter` accepts an optional `idempotency_key`. When omitted, it derives a stable key from the book, chapter and next expected version. An explicit key is available for request-level idempotency.

The durable run store persists the current step, attempt, draft, review, decision, summary and terminal status. A repeated call with the same key returns a completed/terminal run without invoking agents again.

If a process restarts while a run is still `running`, a later call with the same key resumes from the persisted step. Persisted chapter versions are reused when present, which closes the main crash window around version creation.

The current implementation serializes duplicate execution within a process. It does **not** yet provide a cross-process lease/claim protocol, so horizontally concurrent workers require a stronger coordination mechanism before production-scale parallel execution.

### 10. Author approval gates

The outline must be explicitly approved before a chapter can be generated. This is a deterministic application rule and must remain outside the LLM.

The chapter-generation workflow refuses to run when `outline_approved` is false.

### 11. Sequential chapter progression

Chapter generation is scoped to a single chapter. The application is responsible for adding chapters in sequence and validating the outline before generation. The loop does not decide which chapter comes next.

### 12. Failure and observability

A generation run can terminate without producing an accepted summary when:

1. deterministic validation failures exhaust the retry budget;
2. the LLM reviewer rejects the draft until the retry budget is exhausted;
3. a run is marked `needs_review` for human/application handling.

Provider/schema failures are surfaced as explicit errors. Persisted chapter versions, reviews and workflow-run checkpoints provide the current audit trail.

One recovery limitation remains: review persistence and workflow-run checkpointing are currently separate writes. A crash in that small interval can cause the reviewer to be invoked again on resume. A future atomic transaction or review lookup/idempotency constraint should close that gap.

## Architecture boundary

Agents encapsulate LLM-facing capabilities; they do not own business orchestration. Application services/policies own context construction and review decisions. The workflow coordinates these capabilities and persists execution state.

Gemini-specific features remain inside `infrastructure/llm`. The application depends only on provider ports and Pydantic/domain contracts.

LangGraph is an optional orchestration representation, not a domain dependency and not the current durable execution mechanism.
