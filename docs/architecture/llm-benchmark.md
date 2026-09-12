# LLM benchmark

## Purpose

This benchmark compares candidate LLMs on the actual classes of work performed by Book Loop. It is intentionally separate from production routing: benchmark results must not change the default model automatically.

Candidates in the initial snapshot:

- Gemini 3.6 Flash
- Kimi K2.6
- MiniMax M2.7
- DeepSeek V4 Flash

## Workload matrix

| Workload | Primary quality question |
| --- | --- |
| writer | Does the model produce useful prose while respecting canon and constraints? |
| reviewer | Does it detect seeded continuity problems accurately and provide evidence? |
| corrector | Does it fix identified issues without unnecessary changes? |
| summarizer | Does it preserve important facts while compressing the chapter? |
| outline | Does it produce a coherent causal structure under constraints? |
| assertion extraction | Does it extract explicit facts without unsupported inference? |
| linguistic | Does it improve language while preserving meaning and voice? |
| grill | Does it ask a precise, challenging question that helps unblock the author? |

Fixtures are stored in `book_loop/infrastructure/benchmark/fixtures.json`. Every candidate receives the same fixture for a given workload.

## Metrics

Each invocation records:

- success/failure
- wall-clock latency in milliseconds
- input/output token counts when reported by the provider
- token source (`provider` or `estimated`)
- estimated cost using the versioned pricing snapshot
- structured-output validity where applicable
- raw output for later quality assessment
- optional quality score

Provider-reported usage is preferred. An estimated token counter can be supplied for providers that do not expose usage, but those results must not be treated as equivalent to provider-reported usage.

## Quality methodology

Quality is workload-specific. Deterministic checks should be preferred over a generic LLM-as-judge score.

For semantic evaluation, use a fixed rubric and record the rubric version with the results. Human review is preferred for the final routing decision; automated judging can be used as a screening signal but must not be treated as ground truth.

Recommended scoring dimensions:

- **Writer:** canon adherence, continuity, instruction following, prose usefulness.
- **Reviewer:** seeded-issue recall, false-positive rate, evidence quality.
- **Corrector:** issue resolution, preservation of intended content, unnecessary-change rate.
- **Summarizer:** factual coverage, omission rate, compression.
- **Outline:** causal coherence, constraint adherence, scene usefulness.
- **Assertion extraction:** precision, recall, schema validity.
- **Linguistic:** correctness, meaning preservation, voice preservation.
- **Grill:** specificity, usefulness, challenge quality, non-prescriptive behavior.

## Cost methodology

`pricing.json` is a dated snapshot. It is deliberately checked into source control so historical benchmark reports remain interpretable.

The first benchmark uses uncached pricing. Cache-hit economics should be evaluated separately because caching behavior depends on prompt structure and provider capabilities.

## Running a benchmark

The benchmark runner is an infrastructure utility and can be driven by a provider factory from a script or test harness. It does not belong in the domain/application layers.

A live benchmark run must:

1. Select one provider/model explicitly.
2. Load the committed fixtures.
3. Execute every workload independently.
4. Record failures instead of falling back to another model.
5. Persist results with benchmark version and timestamp.
6. Evaluate quality separately from transport metrics.

The production `LLMRouter` must **not** be used in a way that masks a candidate failure during comparison. Fallback is useful in production, but it would invalidate a model comparison.

## Interpretation rules

Do not select a model solely because it has the lowest token price or the highest generic benchmark score. The initial production routing should optimize the workload-specific trade-off between quality, cost, latency and reliability.

A model should only replace the current default for a workload when the benchmark shows a meaningful advantage and the result is not explained by a single outlier run.

## Limitations

- The initial fixture set is intentionally small and should grow as failure modes are discovered.
- Provider latency varies with region, load and time of day.
- Pricing changes must result in a new pricing snapshot.
- A semantic quality score is not directly comparable across unrelated workloads.
- Results from one benchmark date should not be treated as permanent model rankings.
