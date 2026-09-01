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

## Chapter generation

A chapter generation run is scoped to one chapter. The workflow receives the persisted book state and chapter number, builds the relevant canonical context, and coordinates the generation/review loop.

Chapters are generated sequentially: chapter N cannot be generated until chapter N-1 is approved. Chapter 1 has no previous-chapter prerequisite. This rule is enforced by the `GenerateChapter` use case, before the LLM workflow is invoked.

Conceptually:

```text
Book + Chapter objective + Canonical context
                    |
                    v
                 Writer
                    |
                    v
             Draft / candidate
                    |
                    v
              deterministic lint
                    |
                    v
                 Reviewer
                    |
              +-----+-----+
              |           |
           reject       accept
              |           |
              v           v
            retry      Summary
              |           |
              +-----------+
                          v
                 persisted canonical data
```

The exact orchestration implementation is an implementation detail. LangGraph may coordinate the loop, but the use case and domain must not depend on LangGraph APIs.

## Author approval gates

The outline must be explicitly approved before a chapter can be added or generated. This is a deterministic application rule and must remain outside the LLM.

A chapter also requires its immediate predecessor to be approved before generation. This ensures the canonical summary used for continuity comes from an accepted chapter.

## Retry behavior

Retries must be bounded. A failed review should not create an unbounded model-call loop. Previous attempts should remain observable/persisted where the data model supports version history.

## Continuity

The canonical summary of an accepted chapter becomes reusable context for later chapters. Future context should prioritize approved/canonical facts and the author's original intent over transient rejected drafts.
