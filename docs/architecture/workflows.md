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
- the current chapter objective;
- relevant active Canon facts when available.

Rejected drafts are not used as canonical continuity context. Accepted chapter summaries and active Canon facts are the continuity mechanisms for subsequent chapters.

### 2. Writing

`WriterAgent` receives the built context and proposes the chapter draft. Each generated attempt is persisted through `save_chapter_version(book_id, chapter_number, attempt, draft)` before review.

The attempt number starts at `1` for the first generated draft and increments for every retry.

Free-form generation deliberately uses Gemini's normal text output. Structured-output constraints are reserved for capabilities whose result is consumed as typed application data.

### 3. Deterministic validation

`ChapterLinter` runs before the LLM reviewer. A lint failure is treated as a retryable failure while the retry budget remains; after the budget is exhausted the workflow ends in `needs_review` rather than looping indefinitely.

This layer is intentionally deterministic and is not delegated to the LLM.

### 4. Native structured LLM output

The Gemini adapter exposes two provider capabilities:

- `generate()` for free-form text generation;
- `generate_structured()` for typed responses constrained by a JSON Schema derived from a Pydantic model.

The Interactions API `response_format` is used for structured calls, so Gemini is constrained by the schema before the response reaches the application. The JSON is then validated again with Pydantic. This replaces prompt-only JSON conventions and ad-hoc parsing as the primary mechanism.

Gemini 3 generation is configured per capability rather than globally. Structured reviewer/extractor calls use an explicit `thinking_level` and output-token bound, while free-form writing keeps Gemini's model defaults. Sampling parameters such as temperature are intentionally not overridden for Gemini 3.x.

### 5. LLM review and decision policy

For a lint-valid draft, `ReviewerAgent` requests a native structured `SceneReview`. The provider validates the JSON against the schema before returning the typed model.

The reviewer is instructed to evaluate only author-intent fidelity, continuity, coherence and writing quality. It cannot directly mutate the book or Canon.

`application.policies.review.decide()` converts the review result into one of three workflow decisions:

- `accept` — the draft meets the configured review threshold;
- `retry` — the draft is rejected and attempts remain;
- `needs_review` — the retry budget is exhausted and the workflow stops for human/application handling.

The configured `review_threshold` and `max_retries` are application policy, not model output.

### 6. Structured assertion extraction

Canon extraction also uses native structured output. `LLMAssertionExtractor` requests an `ExtractedAssertions` Pydantic wrapper containing `ExtractedAssertion` items.

The adapter validates assertion offsets against the actual source chunk after schema validation. Invalid ranges are rejected before assertions enter the application persistence path.

The extractor can propose assertions and evidence locations, but it cannot promote anything into `CanonicalFact`. Human/application review remains authoritative.

### 7. Retry

A retry returns to `WriterAgent` with the same chapter context and creates a new persisted version. Retries are bounded by `max_retries`; there is no unbounded model-call loop.

Structured-output failures are provider/application failures and can be handled by the same bounded retry/error policy without attempting to repair malformed JSON with regexes.

The persisted attempt/review history is retained so a failed generation remains observable rather than silently replacing previous drafts.

### 8. Summary and canonicalization

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

Structured-output/schema failures are also surfaced as explicit provider/application errors rather than being silently normalized into data.

In all cases, persisted chapter versions and reviews provide the audit trail available to the current repository implementation.

## Architecture boundary

Agents encapsulate LLM-facing capabilities; they do not own business orchestration. Application services/policies own context construction and review decisions. The workflow coordinates these capabilities.

The Gemini-specific features remain inside `infrastructure/llm`. The application depends only on the provider port and Pydantic/domain contracts.

LangGraph currently implements the state-machine execution, but it must remain replaceable. The domain and application layers must not depend on LangGraph-specific state or APIs.
