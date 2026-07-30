"""Tests for runtime environment config (TASK-005). Fully offline."""

from __future__ import annotations

import pytest

from arkmind.runtime import MissingApiKeyError
from arkmind.runtime.config import load_api_key, load_base_url

_API_KEY_ENV = "ARKMIND_LLM_API_KEY"
_BASE_URL_ENV = "ARKMIND_LLM_BASE_URL"
_DEFAULT_BASE_URL = "https://api.openai.com/v1"


def test_load_api_key_returns_value_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_API_KEY_ENV, "sk-test")
    assert load_api_key() == "sk-test"


def test_load_api_key_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(_API_KEY_ENV, raising=False)
    with pytest.raises(MissingApiKeyError):
        load_api_key()


def test_load_api_key_raises_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_API_KEY_ENV, "")
    with pytest.raises(MissingApiKeyError):
        load_api_key()


def test_load_base_url_defaults_to_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(_BASE_URL_ENV, raising=False)
    assert load_base_url() == _DEFAULT_BASE_URL


def test_load_base_url_honours_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_BASE_URL_ENV, "http://localhost:11434/v1")
    assert load_base_url() == "http://localhost:11434/v1"
