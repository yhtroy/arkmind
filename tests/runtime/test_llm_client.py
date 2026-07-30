"""Tests for LLMClient / FakeLLMClient (Runtime Contract v1)."""

from __future__ import annotations

import pytest

from arkmind.runtime import FakeLLMClient, LLMClient


def test_llm_client_is_abstract() -> None:
    with pytest.raises(TypeError):
        LLMClient()  # type: ignore[abstract]


def test_fake_echoes_text_by_default() -> None:
    assert FakeLLMClient().generate(prompt="p", text="hello") == "hello"


def test_fake_returns_canned_response() -> None:
    client = FakeLLMClient(response="canned")
    assert client.generate(prompt="p", text="hello") == "canned"
