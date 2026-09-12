from __future__ import annotations

import json
from typing import TypeVar
from urllib import error, request

from pydantic import BaseModel

from book_loop.domain.protocols import LLMProvider

StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


class OpenAICompatibleProvider(LLMProvider):
    """Small dependency-free adapter for OpenAI-compatible chat-completions APIs.

    This covers providers such as Kimi, MiniMax and DeepSeek without coupling the
    application layer to their SDKs. Provider-specific differences stay in this adapter.
    """

    def __init__(self, *, api_key: str, base_url: str, model: str, timeout_seconds: float = 120.0) -> None:
        if not api_key.strip():
            raise ValueError("An API key is required for an OpenAI-compatible provider")
        if not base_url.strip():
            raise ValueError("A base URL is required for an OpenAI-compatible provider")
        if not model.strip():
            raise ValueError("A model is required for an OpenAI-compatible provider")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def _request(self, payload: dict[str, object]) -> str:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI-compatible provider returned HTTP {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError("OpenAI-compatible provider request failed") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("OpenAI-compatible provider returned an invalid response") from exc
        if isinstance(content, list):
            content = "".join(
                item.get("text", "") for item in content if isinstance(item, dict)
            )
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("OpenAI-compatible provider returned an empty response")
        return content.strip()

    def generate(self, *, system_prompt: str, user_prompt: str, task: str = "default") -> str:
        del task
        return self._request(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
        )

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
        del task
        payload: dict[str, object] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "strict": True,
                    "schema": schema.model_json_schema(),
                },
            },
        }
        if max_output_tokens is not None:
            payload["max_tokens"] = max_output_tokens
        # Keep the semantic setting available to compatible providers that support it.
        if thinking_level != "medium":
            payload["thinking_level"] = thinking_level
        text = self._request(payload)
        try:
            return schema.model_validate_json(text)
        except ValueError as exc:
            raise ValueError(
                f"OpenAI-compatible provider returned structured output that does not match {schema.__name__}"
            ) from exc
