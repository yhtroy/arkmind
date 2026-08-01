"""Tests for NotionClient (M5, Task-003).

Offline tests: the pure ``build_page`` mapping and ``from_env`` config loading
are exercised directly; the network ``create_page`` call is stubbed via
``urllib.request.urlopen`` to verify the returned page id.
"""

from __future__ import annotations

from typing import Self

import pytest

from arkmind.notion import MissingNotionConfigError, NotionClient


class _FakeResponse:
    """Context-manager response stand-in returning canned JSON bytes."""

    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def test_build_page_maps_title_and_content() -> None:
    client = NotionClient(token="secret", database_id="db123")

    page = client.build_page("On Randomness", "Body")

    assert page["parent"] == {"database_id": "db123"}
    props = page["properties"]
    assert isinstance(props, dict)
    assert props["Title"] == {"title": [{"text": {"content": "On Randomness"}}]}
    assert props["Content"] == {"rich_text": [{"text": {"content": "Body"}}]}


def test_build_page_chunks_content_over_rich_text_limit() -> None:
    client = NotionClient(token="secret", database_id="db123")
    long_content = "x" * 4500  # 2000 + 2000 + 500

    page = client.build_page("T", long_content)

    chunks = page["properties"]["Content"]["rich_text"]  # type: ignore[index]
    lengths = [len(chunk["text"]["content"]) for chunk in chunks]
    assert lengths == [2000, 2000, 500]
    assert "".join(chunk["text"]["content"] for chunk in chunks) == long_content


def test_create_page_returns_page_id(monkeypatch: pytest.MonkeyPatch) -> None:
    client = NotionClient(token="secret", database_id="db123")

    def _fake_urlopen(_request: object) -> _FakeResponse:
        return _FakeResponse(b'{"id":"page_123","object":"page"}')

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

    assert client.create_page("On Randomness", "Body") == "page_123"


def test_from_env_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARKMIND_NOTION_TOKEN", raising=False)
    monkeypatch.setenv("ARKMIND_NOTION_DATABASE_ID", "db123")

    with pytest.raises(MissingNotionConfigError) as excinfo:
        NotionClient.from_env()
    assert excinfo.value.variable == "ARKMIND_NOTION_TOKEN"


def test_from_env_requires_database_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARKMIND_NOTION_TOKEN", "secret")
    monkeypatch.delenv("ARKMIND_NOTION_DATABASE_ID", raising=False)

    with pytest.raises(MissingNotionConfigError) as excinfo:
        NotionClient.from_env()
    assert excinfo.value.variable == "ARKMIND_NOTION_DATABASE_ID"


def test_from_env_builds_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARKMIND_NOTION_TOKEN", "secret")
    monkeypatch.setenv("ARKMIND_NOTION_DATABASE_ID", "db123")

    client = NotionClient.from_env()

    assert client.build_page("T", "C")["parent"] == {"database_id": "db123"}
