from __future__ import annotations

from pydantic import BaseModel

from book_loop.infrastructure.llm.router import LLMRoute, LLMRouter


class Payload(BaseModel):
    value: str


class StubProvider:
    def __init__(self, value: str, *, fail: bool = False) -> None:
        self.value = value
        self.fail = fail
        self.calls: list[str] = []

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        del system_prompt, user_prompt
        self.calls.append("generate")
        if self.fail:
            raise RuntimeError("provider unavailable")
        return self.value

    def generate_structured(self, *, system_prompt: str, user_prompt: str, schema, thinking_level="medium", max_output_tokens=None):
        del system_prompt, user_prompt, thinking_level, max_output_tokens
        self.calls.append("structured")
        if self.fail:
            raise RuntimeError("provider unavailable")
        return schema(value=self.value)


def test_router_selects_provider_by_task():
    main = StubProvider("main")
    cheap = StubProvider("cheap")
    router = LLMRouter(
        providers={"main": main, "cheap": cheap},
        routes={"summarizer": LLMRoute(target="cheap")},
        default_route=LLMRoute(target="main"),
    )

    assert router.generate(system_prompt="s", user_prompt="u", task="summarizer") == "cheap"
    assert router.generate(system_prompt="s", user_prompt="u", task="writer") == "main"


def test_router_can_bind_a_semantic_task_without_changing_call_site():
    main = StubProvider("main")
    reasoning = StubProvider("reasoning")
    router = LLMRouter(
        providers={"main": main, "reasoning": reasoning},
        routes={"reviewer": LLMRoute(target="reasoning")},
        default_route=LLMRoute(target="main"),
    )

    reviewer = router.for_task("reviewer")
    assert reviewer.generate(system_prompt="s", user_prompt="u") == "reasoning"
    assert reviewer.generate_structured(system_prompt="s", user_prompt="u", schema=Payload) == Payload(value="reasoning")


def test_router_falls_back_to_main_when_route_provider_fails():
    main = StubProvider("main")
    reasoning = StubProvider("reasoning", fail=True)
    router = LLMRouter(
        providers={"main": main, "reasoning": reasoning},
        routes={"reviewer": LLMRoute(target="reasoning", fallback_target="main")},
        default_route=LLMRoute(target="main"),
    )

    assert router.generate(system_prompt="s", user_prompt="u", task="reviewer") == "main"
    assert reasoning.calls == ["generate"]
    assert main.calls == ["generate"]
