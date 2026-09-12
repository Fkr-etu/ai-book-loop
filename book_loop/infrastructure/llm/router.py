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


class TaskBoundLLMProvider(LLMProvider):
    """Application-facing provider bound to one semantic workload."""

    def __init__(self, router: "LLMRouter", task: str) -> None:
        self._router = router
        self._task = task

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        return self._router.generate(system_prompt=system_prompt, user_prompt=user_prompt, task=self._task)

    def generate_structured(self, *, system_prompt: str, user_prompt: str, schema: type[StructuredModel], thinking_level: str = "medium", max_output_tokens: int | None = None) -> StructuredModel:
        return self._router.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=schema,
            thinking_level=thinking_level,
            max_output_tokens=max_output_tokens,
            task=self._task,
        )


class LLMRouter(LLMProvider):
    """Route LLM calls by workload while keeping provider details in infrastructure."""

    def __init__(self, *, providers: dict[str, LLMProvider], routes: dict[str, LLMRoute], default_route: LLMRoute) -> None:
        if not providers:
            raise ValueError("LLMRouter requires at least one provider")
        self._providers = providers
        self._routes = routes
        self._default_route = default_route

    def for_task(self, task: str) -> TaskBoundLLMProvider:
        return TaskBoundLLMProvider(self, task)

    def _route_for(self, task: str) -> LLMRoute:
        return self._routes.get(task, self._default_route)

    def _provider_for(self, task: str) -> LLMProvider:
        route = self._route_for(task)
        try:
            return self._providers[route.target]
        except KeyError as exc:
            raise RuntimeError(f"No LLM provider configured for target {route.target!r}") from exc

    def _fallback_for(self, task: str) -> LLMProvider | None:
        fallback_target = self._route_for(task).fallback_target
        if not fallback_target:
            return None
        return self._providers.get(fallback_target)

    def generate(self, *, system_prompt: str, user_prompt: str, task: str = "default") -> str:
        provider = self._provider_for(task)
        try:
            return provider.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        except Exception:
            fallback = self._fallback_for(task)
            if fallback is None or fallback is provider:
                raise
            return fallback.generate(system_prompt=system_prompt, user_prompt=user_prompt)

    def generate_structured(self, *, system_prompt: str, user_prompt: str, schema: type[StructuredModel], thinking_level: str = "medium", max_output_tokens: int | None = None, task: str = "default") -> StructuredModel:
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
