# Linguistic validation evaluation

PR 59 establishes a controlled French evaluation corpus and a reproducible category-level evaluation harness before the validation pipeline is integrated into generation.

## Corpus

`tests/fixtures/linguistic_corpus.json` contains deliberately small, versioned examples covering spelling, grammar/agreement, clean text, and literary false-positive cases such as fragments and dialogue.

Each case declares the expected diagnostic categories. Literary cases are explicitly labelled so false positives remain a first-class metric rather than being hidden inside aggregate accuracy.

## Metrics

`book_loop.application.services.linguistic_evaluation.evaluate_checker` reports:

- precision: proportion of detected findings matching an expected category;
- recall: proportion of expected categories detected;
- false positives and false negatives;
- literary false positives and their rate.

The evaluator is checker-agnostic and does not mutate chapters or Canon state.

## Runner

With the optional NLP dependency and French model installed:

```bash
python -m spacy download fr_core_news_sm
python scripts/evaluate_linguistic_validation.py
```

The runner emits JSON so results can later be captured in CI or compared between checker implementations.

## Baseline policy

This PR deliberately does not claim production-quality linguistic accuracy. The corpus is a seed evaluation set, not a statistically representative benchmark. Thresholds should be established only after running the checker on a larger reviewed corpus.

The next iteration should expand coverage for conjugation, agreement, syntax, punctuation, typography, literary dialogue, intentional fragments, archaic language, and parser edge cases. Metrics should then be used to tune diagnostic severity and retry policy rather than maximizing the number of reported warnings.
