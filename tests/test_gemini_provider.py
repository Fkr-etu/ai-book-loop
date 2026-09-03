from __future__ import annotations

import pytest

from book_loop.infrastructure.llm import gemini


class FakeResponse:
    text = "  generated text  "


class FakeModels:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse()


class FakeClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.models = FakeModels()


def test_gemini_provider_uses_system_instruction(monkeypatch):
    client = FakeClient("key")
    monkeypatch.setattr(gemini.genai, "Client", lambda api_key: client)

    provider = gemini.GeminiProvider(api_key="key", model="test-model")
    result = provider.generate(system_prompt="system", user_prompt="user")

    assert result == "generated text"
    assert client.models.calls[0]["model"] == "test-model"
    assert client.models.calls[0]["contents"] == "user"
    assert client.models.calls[0]["config"].system_instruction == "system"


def test_gemini_provider_rejects_missing_configuration():
    with pytest.raises(ValueError, match="API key"):
        gemini.GeminiProvider(api_key="", model="test-model")
    with pytest.raises(ValueError, match="model"):
        gemini.GeminiProvider(api_key="key", model="")


def test_gemini_provider_rejects_empty_response(monkeypatch):
    class EmptyResponse:
        text = ""

    client = FakeClient("key")
    client.models.generate_content = lambda **_: EmptyResponse()
    monkeypatch.setattr(gemini.genai, "Client", lambda api_key: client)

    provider = gemini.GeminiProvider(api_key="key", model="test-model")
    with pytest.raises(RuntimeError, match="empty response"):
        provider.generate(system_prompt="system", user_prompt="user")
