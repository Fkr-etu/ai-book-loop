# Linguistic Validation Pipeline

## 1. Purpose

Book must distinguish objective language errors from stylistic preferences and narrative/canonical problems. The current LLM reviewer is useful for semantic and editorial judgment, but it should not be the sole detector of grammar, conjugation, agreement, spelling, and punctuation errors.

The target architecture is a hybrid validation pipeline:

```text
Generated chapter
      |
      +--> LanguageTool --------> deterministic linguistic diagnostics
      |
      +--> French NLP parser ---> morphology / syntax signals
      |
      +--> Canon checker -------> canonical contradictions
      |
      +--> Gemini reviewer -----> context / style / logic / narrative
      |
      +----------- Diagnostic Fusion -----------+
                              |
                         severity + type
                              |
                    retry / accept / review
```

The objective is **high-value diagnostics**, not the maximum number of warnings.

## 2. Architectural principles

### 2.1 Deterministic checks before probabilistic judgment

Rules and specialized NLP systems should detect objective linguistic anomalies before the LLM reviewer runs. Gemini should contextualize ambiguous cases and assess semantic/editorial quality.

### 2.2 Diagnostics are evidence, not truth

A detector proposes a diagnostic. It does not mutate the chapter automatically.

A diagnostic must contain enough provenance to explain where it came from and why it was produced.

### 2.3 Never silently rewrite generated content

The validation pipeline must not automatically replace text merely because a tool proposed a correction. Corrections are proposals that may be accepted by a later policy or by the author.

### 2.4 Preserve literary freedom

French literary text legitimately contains dialogue, oral language, fragments, deliberate repetitions, invented words, archaic forms, metaphors, and stylistic deviations. False positives must therefore be treated as a first-class risk.

### 2.5 Canon remains authoritative for project truth

Language validation and Canon validation are complementary:

- LanguageTool answers: "Does this text contain a likely language error?"
- NLP answers: "Are the grammatical/morphological structures compatible?"
- Canon answers: "Does this contradict approved project knowledge?"
- Gemini answers: "Does this make sense in context and satisfy the author's intent?"

No retrieval layer or LLM response becomes canonical truth by itself.

## 3. Diagnostic model

Introduce a common diagnostic abstraction at the application boundary.

Suggested model:

```python
class DiagnosticCategory(StrEnum):
    SPELLING = "spelling"
    GRAMMAR = "grammar"
    CONJUGATION = "conjugation"
    AGREEMENT = "agreement"
    SYNTAX = "syntax"
    PUNCTUATION = "punctuation"
    TYPOGRAPHY = "typography"
    STYLE = "style"
    REPETITION = "repetition"
    CLARITY = "clarity"
    CONTINUITY = "continuity"
    CANON = "canon"
    LOGIC = "logic"
    CHARACTER = "character"
    TIMELINE = "timeline"

class DiagnosticSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"

class DiagnosticSource(StrEnum):
    LINGUISTIC_LINTER = "linguistic_linter"
    NLP = "nlp"
    CANON = "canon"
    LLM = "llm"
    FUSION = "fusion"

class Diagnostic(BaseModel):
    category: DiagnosticCategory
    severity: DiagnosticSeverity
    source: DiagnosticSource
    message: str
    start_offset: int | None = None
    end_offset: int | None = None
    original_text: str | None = None
    suggestions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    rule_id: str | None = None
    related_assertion_id: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
```

The exact model can evolve, but diagnostics should remain provider-neutral.

## 4. Layer 1: LanguageTool

### Role

Use LanguageTool as the first linguistic detector for French spelling, grammar, agreement, conjugation, punctuation, and typography.

It is a specialized grammar-checking engine and should be treated as a detector, not as an automatic rewrite engine.

### Integration strategy

Hide LanguageTool behind an application port such as:

```python
class LinguisticChecker(Protocol):
    def check(self, text: str, *, language: str = "fr") -> list[Diagnostic]: ...
```

The infrastructure adapter converts LanguageTool responses into domain/application-neutral diagnostics.

### Requirements

- default language: `fr`;
- preserve offsets from the checked text;
- preserve rule IDs and suggested replacements;
- distinguish errors from style/typography warnings where possible;
- make the checker replaceable;
- avoid coupling domain models to LanguageTool response structures.

### Deployment

Prefer a local/self-hosted LanguageTool service for development and controlled production environments when licensing/operational requirements permit it. A remote API may be used as an adapter later, but provider/network failure must not corrupt chapter state.

Configuration should be explicit, for example:

```text
LINGUISTIC_CHECKER=language_tool
LANGUAGE_TOOL_URL=http://localhost:8010
LANGUAGE_TOOL_LANGUAGE=fr
```

Do not introduce a mandatory external dependency into the core domain.

## 5. Layer 2: French NLP parsing

Use a French NLP parser such as spaCy's French pipeline as a structural analysis layer.

The initial objective is not to build a second grammar checker. It is to expose:

- tokens;
- lemmas;
- part-of-speech tags;
- morphology;
- dependency relations;
- sentence boundaries;
- named entities.

This enables deterministic or semi-deterministic checks that require structure.

Examples:

```text
Les chevalier avançait.
```

Potential structural signals:

```text
DET: plural
NOUN: singular
VERB: singular
```

The parser can flag a likely number-agreement inconsistency without asking an LLM to rediscover the same structure.

### Important limitation

French literary language contains constructions that general-purpose parsers may handle imperfectly. Parser output must therefore be treated as evidence with confidence, not absolute truth.

## 6. Layer 3: Canon validation

Canon validation should remain independent from linguistic validation.

Given a generated chapter:

```text
chapter
  -> assertions / facts
  -> compare against active Canon
  -> canonical diagnostics
```

Example:

```text
Chapter: "Marie vit désormais à Lyon."
Canon:   Marie lives in Marseille.
```

This is a `CANON` diagnostic, not a grammar error.

The diagnostic should reference the canonical assertion when available so that the author can inspect the evidence and approval history.

## 7. Layer 4: Gemini contextual review

Gemini remains responsible for problems that require broad context or literary judgment:

- narrative logic;
- author-intent compliance;
- scene quality;
- character consistency;
- temporal consistency;
- style;
- clarity;
- repetition;
- interpretation of ambiguous linguistic diagnostics.

The reviewer should receive existing deterministic diagnostics as structured input rather than being asked to rediscover all language errors from scratch.

For ambiguous cases, the reviewer may classify a detector result as:

```text
KEEP      intentional literary/oral construction
CONFIRM   likely genuine issue
DOWNGRADE  useful but non-blocking suggestion
```

The LLM must not silently modify canonical state.

## 8. Diagnostic fusion

The application needs a deterministic fusion step.

Inputs:

```text
LanguageTool diagnostics
NLP diagnostics
Canon diagnostics
LLM diagnostics
```

Outputs:

```text
unique, normalized diagnostics
```

Fusion responsibilities:

1. merge duplicate diagnostics referring to the same text span;
2. preserve all relevant sources;
3. choose the highest justified severity;
4. retain confidence and provenance;
5. prevent one noisy provider from generating repeated retry signals;
6. distinguish objective errors from suggestions.

Example:

```text
LanguageTool: agreement error
NLP:          morphology mismatch
LLM:          confirms genuine error
```

should become one `AGREEMENT / ERROR` diagnostic with multiple evidence sources.

## 9. Severity policy

The first version should use conservative rules.

### ERROR

Use when the system has strong evidence that the text is objectively incorrect or violates an explicit invariant.

Examples:

- clear spelling error;
- clear subject/verb agreement error;
- malformed grammar strongly confirmed by multiple signals;
- explicit Canon contradiction.

### WARNING

Use when the issue is plausible but context-dependent.

Examples:

- ambiguous grammar result;
- parser uncertainty;
- possible repetition;
- unusual literary construction.

### SUGGESTION

Use for editorial improvement without claiming the text is wrong.

Examples:

- sentence could be shorter;
- repeated adjective;
- stylistic alternative.

## 10. Retry policy

Do not trigger a generation retry for every diagnostic.

A retry should be triggered only when the application policy determines that the accumulated diagnostics represent a material defect.

Suggested initial policy:

```text
ERROR + high confidence
        -> retry candidate

WARNING
        -> reviewer/author context

SUGGESTION
        -> never automatic retry
```

Canon contradictions should be handled separately because the correct action may be author review rather than regeneration.

## 11. Test strategy

Create a small controlled French evaluation corpus before optimizing the implementation.

### Category A — conjugation

Examples should cover:

- person mismatch;
- tense mismatch;
- common irregular verbs;
- auxiliary selection;
- participles.

### Category B — agreement

Cover:

- subject/verb number;
- noun/adjective gender;
- noun/adjective number;
- past participle agreement where applicable.

### Category C — spelling and typography

Cover:

- common misspellings;
- apostrophes;
- punctuation;
- quotation marks;
- dialogue formatting.

### Category D — intentional deviations

Include:

- dialogue contractions;
- slang;
- fragments;
- invented words;
- poetic syntax;
- metaphors;
- character-specific speech.

### Category E — Canon

Include:

- direct contradiction;
- compatible restatement;
- unresolved conflict;
- rejected assertion that must not become Canon.

### Metrics

Track at minimum:

```text
precision
recall
false-positive rate
false-negative rate
retry precision
```

For Book, **precision is especially important** because noisy corrections damage author trust.

## 12. Observability

Persist or log diagnostics in a way that allows later evaluation.

For each diagnostic, retain:

- detector source;
- rule/provider identifier;
- category;
- severity;
- confidence;
- text offsets;
- original text;
- suggested replacement(s);
- final reviewer decision when applicable.

This allows us to answer:

- Which detector catches the most real errors?
- Which rules create the most false positives?
- Which diagnostics cause unnecessary retries?
- Does the LLM improve or worsen linguistic decisions?

This dataset can later become the foundation for custom rules or a specialized GEC model if the scale justifies it.

## 13. Failure handling

A failure of the linguistic checker must not make a valid chapter disappear or corrupt its persisted version history.

Recommended policy:

```text
LanguageTool unavailable
        -> record checker failure
        -> continue with remaining validation layers
        -> do not silently claim linguistic validation passed
```

Similarly, an NLP parser failure should degrade gracefully.

The distinction must remain visible between:

```text
NO_ISSUES_FOUND
```

and

```text
CHECK_NOT_AVAILABLE
```

## 14. Implementation boundaries

Recommended package structure:

```text
book_loop/
  application/
    services/
      diagnostics.py
      linguistic_validation.py
    use_cases/
      validate_chapter.py
  domain/
    models.py
    protocols.py
  infrastructure/
    linguistic/
      languagetool.py
      spacy.py
  agents/
    reviewer.py
```

Exact paths may be adapted to the current repository structure. The important rule is that LanguageTool and spaCy remain infrastructure adapters behind application ports.

## 15. Phased technical plan

### Phase 0 — Spike and baseline

**Goal:** measure the current reviewer and establish a baseline.

Tasks:

1. Build a controlled French evaluation corpus.
2. Run the existing Reviewer against it.
3. Record precision/recall and false positives.
4. Identify the exact classes of errors currently missed in generated chapters.
5. Define acceptance thresholds for the new pipeline.

**Deliverable:** evaluation dataset + baseline report.

### Phase 1 — LanguageTool adapter

**Goal:** add deterministic linguistic diagnostics without changing generation behavior.

Tasks:

1. Add `LinguisticChecker` application port.
2. Implement LanguageTool infrastructure adapter.
3. Map provider responses to `Diagnostic`.
4. Preserve offsets, rule IDs, suggestions and confidence.
5. Add unit tests with fake checker.
6. Add integration tests against a local LanguageTool service if CI can support it.
7. Add configuration and health/error handling.

**Deliverable:** standalone chapter linguistic validation service.

### Phase 2 — Diagnostic model and fusion

**Goal:** create one provider-neutral diagnostic contract.

Tasks:

1. Add category/severity/source enums.
2. Add `Diagnostic` model.
3. Implement duplicate detection and span normalization.
4. Define retry-relevant severity rules.
5. Expose diagnostics from chapter validation.
6. Ensure existing Reviewer behavior remains backward compatible.

**Deliverable:** unified diagnostics API.

### Phase 3 — French NLP structural layer

**Goal:** add morphology/syntax signals where LanguageTool alone is insufficient.

Tasks:

1. Evaluate spaCy French pipeline on the corpus.
2. Add parser adapter.
3. Implement only high-confidence structural checks initially.
4. Compare results against LanguageTool.
5. Fuse overlapping findings.
6. Measure false positives on literary/dialogue samples.

**Deliverable:** second independent linguistic signal source.

### Phase 4 — Contextual Gemini review

**Goal:** make the LLM reviewer contextualize diagnostics instead of rediscovering everything.

Tasks:

1. Extend reviewer input with structured diagnostics.
2. Ask Gemini to confirm, downgrade or dismiss ambiguous linguistic findings.
3. Keep semantic/editorial review responsibilities.
4. Persist reviewer reasoning/decision metadata where appropriate.
5. Add tests proving deterministic errors survive contextual review.

**Deliverable:** hybrid linguistic + semantic review.

### Phase 5 — Canon integration

**Goal:** unify language QA and knowledge QA.

Tasks:

1. Generate Canon diagnostics from active facts/assertions.
2. Link diagnostics to assertion IDs.
3. Keep Canon contradictions separate from language errors.
4. Add conflict-aware retry/review policies.
5. Verify that rejected/deferred assertions never become blocking Canon truth.

**Deliverable:** chapter validation against both language and Canon.

### Phase 6 — Workflow integration

**Goal:** make the pipeline influence the Writer → Review → Retry loop safely.

Tasks:

1. Run deterministic checks before LLM review.
2. Pass diagnostics to Reviewer.
3. Apply retry policy only to blocking defects.
4. Persist every generated version and review.
5. Keep reruns version-safe.
6. Add E2E regression for language error → retry → corrected version.

**Deliverable:** restart-safe hybrid generation loop.

### Phase 7 — Evaluation and tuning

**Goal:** optimize author trust rather than raw detection count.

Tasks:

1. Expand the evaluation corpus from real generated chapters.
2. Measure each detector independently.
3. Tune severity thresholds.
4. Add ignore/allow-list mechanisms for intentional literary forms.
5. Track retry precision.
6. Identify high-value custom rules.

**Deliverable:** measurable quality gate for generated chapters.

## 16. What not to build yet

Do not initially build:

- a custom grammar model;
- fine-tuning of Gemini for grammar correction;
- a vector database for linguistic validation;
- automatic rewriting of every detected error;
- a second large LLM solely to validate the first LLM;
- a complex linguistic knowledge graph.

These may become justified later if evaluation data demonstrates a real gap.

## 17. Future evolution

If Book eventually accumulates a large corpus of accepted/rejected diagnostics, that dataset can support:

```text
observed diagnostics
        ↓
false-positive analysis
        ↓
custom rules
        ↓
small specialized models
        ↓
optional GEC model
```

The architecture should therefore preserve detector provenance and human decisions from day one.

## 18. Definition of done

The first production-worthy iteration is complete when:

- grammar/conjugation errors are detected independently of the LLM;
- diagnostics contain exact text locations;
- LanguageTool failures degrade safely;
- literary/dialogue false positives are measured;
- Gemini receives structured diagnostics for contextual judgment;
- Canon contradictions are represented separately;
- retries occur only for policy-defined blocking defects;
- every generated version remains persisted and immutable;
- the E2E workflow proves detection, retry, persistence and final acceptance;
- quality metrics are recorded and reproducible.
