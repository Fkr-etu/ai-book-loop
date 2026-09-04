# Linguistic validation — Phase 1/2 implementation

This implementation establishes the provider-neutral diagnostic contract and the first external linguistic detector without changing the generation workflow yet.

## Included

- `Diagnostic` model with category, severity, source, offsets, original text, suggestions, confidence and provenance metadata.
- Explicit `NO_ISSUES_FOUND`, `ISSUES_FOUND` and `CHECK_NOT_AVAILABLE` states.
- `LinguisticValidationService` that aggregates independent checkers and performs deterministic fusion.
- LanguageTool HTTP adapter using `/v2/check` and French as the default language.
- LanguageTool rule IDs and replacement suggestions are preserved.
- Provider/network failures degrade to `CHECK_NOT_AVAILABLE` and never masquerade as a clean validation.
- Duplicate findings are merged deterministically; highest severity and highest confidence win, while suggestions and provider provenance are preserved.
- Empty chapter text is treated as a blocking application invariant.

## Deliberate boundaries

This PR does **not** yet wire linguistic validation into Writer → Reviewer → Corrector. It also does not add spaCy, Canon diagnostics or Gemini contextual classification. Those remain separate phases from the architecture defined in `linguistic-validation.md`.

This keeps the first runtime addition independently testable and avoids introducing a mandatory network service or large NLP model into CI.

## Configuration

```text
LINGUISTIC_CHECKER=disabled
LANGUAGE_TOOL_URL=http://localhost:8010
LINGUISTIC_LANGUAGE=fr
```

The checker remains disabled by default until the deployment provides a LanguageTool service. The application core has no dependency on LanguageTool's response types.
