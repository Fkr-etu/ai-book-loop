# Linguistic validation — Phase 0/1/2/3 implementation

This implementation establishes the provider-neutral diagnostic contract, the first external linguistic detector, a labelled French evaluation corpus, baseline metric computation, and a conservative spaCy structural detector. The generation workflow is still unchanged.

## Included

- `Diagnostic` model with category, severity, source, offsets, original text, suggestions, confidence and provenance metadata.
- Explicit `NO_ISSUES_FOUND`, `ISSUES_FOUND` and `CHECK_NOT_AVAILABLE` states.
- `LinguisticValidationService` that aggregates independent checkers and performs deterministic fusion.
- LanguageTool HTTP adapter using `/v2/check` and French as the default language.
- LanguageTool rule IDs and replacement suggestions are preserved.
- Provider/network failures degrade to `CHECK_NOT_AVAILABLE` and never masquerade as a clean validation.
- Duplicate findings are merged deterministically; highest severity and highest confidence win, while suggestions and provider provenance are preserved.
- Empty chapter text is treated as a blocking application invariant.
- Optional spaCy dependency and `SpacyFrenchChecker` infrastructure adapter.
- Conservative French spaCy signals: subject/verb number disagreement as an error and verb-less sentence structures as warnings.
- Lazy spaCy model loading so the base application and CI do not require the NLP model.
- A small labelled French corpus covering spelling, grammar, agreement and literary/dialogue false-positive samples.
- A provider-neutral evaluation service reporting precision, recall, false positives, false negatives and literary false positives.

## Deliberate boundaries

This PR does **not** yet wire linguistic validation into Writer → Reviewer → Corrector. It also does not add Canon diagnostics or Gemini contextual classification. Those remain separate phases from the architecture defined in `linguistic-validation.md`.

The spaCy layer intentionally starts with high-confidence structural signals. It does not attempt general grammar correction or automatic rewriting. Literary fragments are warnings rather than blocking errors because fragments are often intentional in prose and dialogue.

## Configuration

```text
LINGUISTIC_CHECKER=disabled
LANGUAGE_TOOL_URL=http://localhost:8010
LINGUISTIC_LANGUAGE=fr
SPACY_MODEL=fr_core_news_sm
```

The linguistic checker remains disabled by default. spaCy is an optional `nlp` dependency and the French model is loaded only when the adapter is used.

## Evaluation baseline

The corpus lives at `tests/fixtures/linguistic_corpus.json`. It is deliberately small and version-controlled so the baseline is reproducible. The evaluation service is detector-agnostic and can be reused when the corpus grows from real generated chapters.

Current metrics are category-level metrics; exact span correctness is validated separately by the diagnostic contract tests. The corpus also includes literary fragments and dialogue specifically to make false-positive cost visible before any detector is allowed to drive retries.

## Next phase

The next implementation step is Gemini contextual review: deterministic findings should be supplied as structured diagnostics and Gemini should confirm, downgrade or dismiss ambiguous findings without becoming the source of truth for offsets or Canon state.
