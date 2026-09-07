# Workflows

## Book lifecycle

```text
CreateBook
  -> GenerateOutline
  -> author approves outline
  -> AddChapter (sequentially)
  -> GenerateChapter
  -> deterministic / linguistic validation
  -> review
  -> accepted summary
  -> consistency / Canon review as applicable
  -> next chapter
```

The application owns state transitions and approval rules. The LLM proposes content and assessments; it does not decide whether author approval or Canon promotion has happened.

## Chapter generation loop

A generation run is scoped to one chapter. The workflow receives persisted book state and chapter number, builds bounded context, and coordinates Writer → validation → Reviewer → Retry/Correction → Summary.

`ChapterWorkflow.run()` is the production execution path. It uses durable persisted workflow-run state. `build()` remains a LangGraph-compatible representation, but it is not the durable execution mechanism.

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
deterministic + linguistic validation
       |
       +------ blocking ------> bounded retry / failure
       |
       v
    Reviewer
       |
       +---- retry ----> Corrector ----+
       |                               |
       +---- accept ---> Summarizer ----+
       |                               |
       +---- needs_review ----------> END
```

Each meaningful state transition is checkpointed. A workflow run is identified by `(book_id, chapter_number, idempotency_key)`.

## Consistency and Canon lifecycle

Consistency is a complementary quality layer, not an automatic Canon authority:

```text
approved/imported material
          |
          v
   assertion extraction
          |
          v
 assertions + evidence
      /          \
     v            v
assertion-vs-   new-text-vs-
assertion       active Canon
conflicts       diagnostics
      \          /
       v        v
   consistency issues
          |
          v
  author/application review
          |
          v
        Canon
```

`DetectConflicts` persists assertion-vs-assertion conflicts. `CanonDiagnosticChecker` reports contradictions between newly supplied text and active Canon facts. `UnifiedConsistencyEngine` composes detector implementations and deduplicates stable `ConsistencyIssue` results. Detectors currently execute sequentially.

No detector decides which conflicting assertion is true. Promotion to Canon requires an explicit review decision.

## Context construction

`ContextBuilder` creates bounded prompt context from persisted book state and approved Canon context when configured. It includes author intent, theme, lore, structured outline, constraints, previous accepted chapter summaries, current chapter objective and relevant active Canon facts.

Rejected drafts are not used as canonical continuity context.

## Writing and validation

The workflow reserves the next attempt number before invoking the Writer. Generated attempts are persisted before review. Deterministic linting and configured linguistic validation run before LLM review.

Blocking diagnostics prevent reviewer execution. Non-blocking diagnostics are passed as structured input. Provider/schema failures surface as explicit errors rather than being treated as a clean result.

## Review and decision policy

`ReviewerAgent` returns a structured review. `application.policies.review.decide()` converts it into `accept`, `retry`, or `needs_review` according to application thresholds, attempt count and retry budget. These rules are not delegated to the model.

## Retry and correction

A retry moves the run to `correct`. `CorrectorAgent` receives the current draft and persisted review, and the corrected draft is stored as a new immutable chapter version. Review/decision fields are cleared before returning to review. Retries are bounded.

## Summary and chapter approval

When review accepts a draft, `SummarizerAgent` produces the chapter summary and the workflow persists the accepted chapter state. Approved chapter material can then feed assertion extraction and consistency analysis according to the Canon workflow.

## Restart and idempotency

`GenerateChapter` accepts an optional `idempotency_key`. Durable workflow state records the current step, attempt, draft, review, decision, summary and terminal status. Repeated calls with the same key do not intentionally replay a terminal run.

The current implementation serializes duplicate execution within a process. It does not yet provide a cross-process lease/claim protocol, so horizontally concurrent workers require stronger coordination.

## Author approval gates

The outline must be explicitly approved before chapter generation. Canon promotion likewise requires an explicit review decision. Both are deterministic application rules and remain outside the LLM.

## Failure and observability

Runs can terminate without an accepted summary when deterministic validation or review exhausts the retry budget, or when human/application handling is required. Persisted chapter versions, reviews, Canon decisions and workflow checkpoints provide the current audit trail.

A small recovery gap remains where review persistence and workflow checkpointing are separate writes; atomic transaction/idempotency work can close that interval later.

## Architecture boundary

Agents encapsulate LLM-facing capabilities; application services/policies own deterministic business decisions and context construction; workflows coordinate execution and persistence; consistency detectors report evidence-backed issues; explicit review controls Canon.

Gemini-specific features remain inside infrastructure. LangGraph is an optional orchestration representation, not a domain dependency and not the current durable execution mechanism.
