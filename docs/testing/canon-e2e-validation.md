# Canon E2E Validation

The `Canon E2E Validation` GitHub Actions workflow is a manual regression gate for the Canon-to-generation loop.

From GitHub Actions, run the workflow with the default scenario **Les Veilleurs de Marseille**.

The validation covers, in order:

1. extraction of an assertion from an approved chapter;
2. human validation of the assertion;
3. promotion to an active `CanonicalFact`;
4. construction of a new chapter-generation context;
5. verification that the active Canon fact is present in the writer prompt.

The scenario uses deterministic test doubles for the extractor and LLM. It therefore validates the application/infrastructure wiring without consuming Gemini API quota. The existing `Real Book Run` workflow remains the place for live Gemini generation.
