from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from pydantic import BaseModel

from book_loop.domain.protocols import LLMProvider

StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


@dataclass(frozen=True)
class LLMRoute:
    target: str
    fallback_target: str | None = None


class LLMRouter(LLMProvider):
    """Route LLM calls by workload while keeping provider details in infrastructure.

    The router is intentionally deterministic: application code selects a semantic task
    (writer, reviewer, summarizer, etc.), while configuration decides which model handles it.
    A target may optionally define a fallback target for transient provider failures.
    """

    def __init__(
        self,
        *,
        providers: dict[str, LLMProvider],
        routes: dict[str, LLMRoute],
        default_route: LLMRoute,
    ) -> None:
        if not providers:
            raise ValueError("LLMRouter requires at least one provider")
        self._providers = providers
        self._routes = routes
        self._default_route = default_route

    def _provider_for(self, task: str) -> LLMProvider:
        route = self._routes.get(task, self._default_route)
        try:
            return self._providers[route.target]
        except KeyError as exc:
            raise RuntimeError(f"No LLM provider configured for target {route.target!r}") from exc

    def _fallback_for(self, task: str) -> LLMProvider | None:
        route = self._routes.get(task, self._default_route)
        if not route.fallback_target:
            return None
        return self._providers.get(route.fallback_target)

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        task: str = "default",
    ) -> str:
        provider = self._provider_for(task)
        try:
            return provider.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        except Exception:
            fallback = self._fallback_for(task)
            if fallback is None or fallback is provider:
                raise
            return fallback.generate(system_prompt=system_prompt, user_prompt=user_prompt)

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[StructuredModel],
        thinking_level: str = "medium",
        max_output_tokens: int | None = None,
        task: str = "default",
    ) -> StructuredModel:
        provider = self._provider_for(task)
        try:
            return provider.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema,
                thinking_level=thinking_level,
                max_output_tokens=max_output_tokens,
            )
        except Exception:
            fallback = self._fallback_for(task)
            if fallback is None or fallback is provider:
                raise
            return fallback.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema,
                thinking_level=thinking_level,
                max_output_tokens=max_output_tokens,
            )
