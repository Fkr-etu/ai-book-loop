# Reviewer structured output

The reviewer LLM is expected to return JSON matching `SceneReview`. Because LLMs can occasionally emit Python-style objects, bare JSON keys, or fenced JSON despite the prompt, `ReviewerAgent` normalizes these safe structured-data variants before Pydantic validation.

The fallback uses `ast.literal_eval`, never `eval`, so only literal data structures are accepted. Invalid or non-object output still fails explicitly with `Reviewer returned invalid structured output`.

Reviewer scores are numeric values from 0 to 10 and may be fractional (for example, `8.5`).
