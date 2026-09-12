from __future__ import annotations

from book_loop.domain.protocols import LLMProvider
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.llm.fake import FakeLLMProvider
from book_loop.infrastructure.llm.gemini import GeminiProvider
from book_loop.infrastructure.llm.openai_compatible import OpenAICompatibleProvider
from book_loop.infrastructure.llm.router import LLMRoute, LLMRouter


def _provider_for_target(settings: Settings, target: str) -> LLMProvider | None:
    provider_name, separator, model = target.partition(":")
    if not separator or not model:
        raise ValueError(f"Invalid LLM router target {target!r}; expected provider:model")

    if provider_name == "gemini":
        if not settings.gemini_api_key:
            return None
        return GeminiProvider(api_key=settings.gemini_api_key, model=model)

    provider_configs = {
        "kimi": (settings.kimi_api_key, settings.kimi_base_url),
        "minimax": (settings.minimax_api_key, settings.minimax_base_url),
        "deepseek": (settings.deepseek_api_key, settings.deepseek_base_url),
    }
    if provider_name in provider_configs:
        api_key, base_url = provider_configs[provider_name]
        if not api_key:
            return None
        return OpenAICompatibleProvider(api_key=api_key, base_url=base_url, model=model)

    raise ValueError(f"Unsupported LLM router provider {provider_name!r}")


def create_llm(settings: Settings, *, model: str | None = None) -> LLMProvider:
    if settings.llm_provider == "fake" or not settings.gemini_api_key:
        return FakeLLMProvider()

    if settings.llm_router_enabled and model is None:
        providers: dict[str, LLMProvider] = {}
        for target_name, target in settings.llm_router_targets.items():
            provider = _provider_for_target(settings, target)
            if provider is not None:
                providers[target_name] = provider

        if not providers:
            return FakeLLMProvider()

        routes = {
            task: LLMRoute(
                target=target,
                fallback_target="main" if target != "main" and "main" in providers else None,
            )
            for task, target in settings.llm_router_routes.items()
        }
        default_target = settings.llm_router_default_target
        if default_target not in providers:
            raise ValueError(f"LLM router default target {default_target!r} is not configured")
        return LLMRouter(
            providers=providers,
            routes=routes,
            default_route=LLMRoute(target=default_target),
        )

    if settings.llm_provider == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key, model=model or settings.llm_model)
    return FakeLLMProvider()
