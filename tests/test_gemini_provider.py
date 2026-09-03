from __future__ import annotations

import pytest

from book_loop.infrastructure.llm import gemini


class FakeResponse:
    output_text = "  generated text  "


class FakeInteractions:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse()


class FakeClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.interactions = FakeInteractions()


def test_gemini_provider_uses_interactions_api(monkeypatch):
    client = FakeClient("key")
    monkeypatch.setattr(gemini.genai, "Client", lambda api_key: client)

    provider = gemini.GeminiProvider(api_key="key", model="test-model")
    result = provider.generate(system_prompt="system", user_prompt="user")

    assert result == "generated text"
    assert client.interactions.calls[0] == {
        "model": "test-model",
        "input": "user",
        "system_instruction": "system",
    }


def test_gemini_provider_rejects_missing_configuration():
    with pytest.raises(ValueError, match="API key"):
        gemini.GeminiProvider(api_key="", model="test-model")
    with pytest.raises(ValueError, match="model"):
        gemini.GeminiProvider(api_key="key", model="")


def test_gemini_provider_rejects_empty_response(monkeypatch):
    class EmptyResponse:
        output_text = ""

    client = FakeClient("key")
    client.interactions.create = lambda **_: EmptyResponse()
    monkeypatch.setattr(gemini.genai, "Client", lambda api_key: client)

    provider = gemini.GeminiProvider(api_key="key", model="test-model")
    with pytest.raises(RuntimeError, match="empty response"):
        provider.generate(system_prompt="system", user_prompt="user")
