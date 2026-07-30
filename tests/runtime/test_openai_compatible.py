"""Tests for OpenAICompatibleClient (TASK-005). Fully offline — no network.

A lightweight stub stands in for the ``openai.OpenAI`` client so the provider's
request shaping and response handling are verified without any HTTP call.
"""

from __future__ import annotations

from typing import Any

from arkmind.runtime import ModelConfig
from arkmind.runtime.providers import OpenAICompatibleClient


class _StubMessage:
    def __init__(self, content: str | None) -> None:
        self.content = content


class _StubChoice:
    def __init__(self, content: str | None) -> None:
        self.message = _StubMessage(content)


class _StubResponse:
    def __init__(self, content: str | None) -> None:
        self.choices = [_StubChoice(content)]


class _StubCompletions:
    def __init__(self, content: str | None) -> None:
        self._content = content
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> _StubResponse:
        self.calls.append(kwargs)
        return _StubResponse(self._content)


class _StubChat:
    def __init__(self, content: str | None) -> None:
        self.completions = _StubCompletions(content)


class _StubClient:
    def __init__(self, content: str | None) -> None:
        self.chat = _StubChat(content)


def test_generate_returns_model_content() -> None:
    stub = _StubClient("核心概念")
    client = OpenAICompatibleClient(ModelConfig(model="gpt-x"), stub)  # type: ignore[arg-type]
    assert client.generate("system prompt", "body text") == "核心概念"


def test_generate_maps_prompt_and_text_to_messages() -> None:
    stub = _StubClient("ok")
    client = OpenAICompatibleClient(ModelConfig(model="gpt-x", temperature=0.0), stub)  # type: ignore[arg-type]
    client.generate("PROMPT", "TEXT")
    call = stub.chat.completions.calls[0]
    assert call["model"] == "gpt-x"
    assert call["temperature"] == 0.0
    assert call["messages"] == [
        {"role": "system", "content": "PROMPT"},
        {"role": "user", "content": "TEXT"},
    ]


def test_generate_returns_empty_string_when_content_none() -> None:
    stub = _StubClient(None)
    client = OpenAICompatibleClient(ModelConfig(model="gpt-x"), stub)  # type: ignore[arg-type]
    assert client.generate("p", "t") == ""


def test_is_an_llm_client() -> None:
    from arkmind.runtime import LLMClient

    assert issubclass(OpenAICompatibleClient, LLMClient)
