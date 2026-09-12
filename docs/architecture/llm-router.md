# LLM Router

## Purpose

Book Loop keeps LLMs behind the `LLMProvider` port and can optionally route each workload to a different model/provider. This is an infrastructure concern: domain and application code do not depend on Gemini, Kimi, MiniMax or DeepSeek APIs.

The router is disabled by default, so the existing Gemini configuration remains unchanged.

## Routing model

Workloads are expressed as semantic task names:

- `writer`: chapter generation
- `reviewer`: chapter review / coherence analysis
- `corrector`: editorial correction
- `summarizer`: canonical chapter summary
- `outline`: outline generation
- `grill`: Critical Eye / Grill
- `assertion_extraction`: Canon extraction
- `linguistic`: contextualization of deterministic linguistic diagnostics

`Container` binds each application component to a task-specific view of the router. Existing agents therefore keep the same `LLMProvider` contract.

## Targets

A target is configured as `provider:model`, for example:

```text
main=gemini:gemini-3.6-flash
reasoning=kimi:<model-id>
cheap=minimax:<model-id>
```

Supported infrastructure adapters in this first version:

- `gemini`: native Google GenAI adapter
- `kimi`: OpenAI-compatible adapter
- `minimax`: OpenAI-compatible adapter
- `deepseek`: OpenAI-compatible adapter

The compatible adapter deliberately avoids vendor SDK dependencies. Provider-specific reasoning controls should be added to dedicated adapters rather than leaking into the application port.

## Fallback

Non-main routes may fall back to `main` when the selected provider raises an exception. This is a resilience mechanism, not a quality arbitration system. Later iterations should distinguish retryable transport/rate-limit failures from invalid model output before enabling more aggressive fallback policies.

## Configuration

Enable with:

```env
LLM_ROUTER_ENABLED=true
```

Targets and task mappings are Pydantic settings dictionaries and can be supplied as JSON environment variables. Example:

```env
LLM_ROUTER_TARGETS={"main":"gemini:gemini-3.6-flash","cheap":"minimax:<model-id>","reasoning":"kimi:<model-id>"}
LLM_ROUTER_ROUTES={"writer":"main","reviewer":"reasoning","corrector":"main","summarizer":"cheap","grill":"reasoning","outline":"cheap","assertion_extraction":"cheap","linguistic":"cheap","default":"main"}
```

Provider credentials remain separate secrets (`GEMINI_API_KEY`, `KIMI_API_KEY`, `MINIMAX_API_KEY`, `DEEPSEEK_API_KEY`).

## Deliberate non-goals

This first version does not implement:

- automatic cost estimation before a request;
- dynamic routing based on token budget;
- quality scoring or A/B experimentation;
- provider health checks;
- prompt caching abstraction;
- vendor-specific thinking controls;
- usage/cost telemetry.

Those should follow once real workflows are measured. The router is intentionally a small seam that makes those capabilities possible without moving provider concerns into the application layer.
