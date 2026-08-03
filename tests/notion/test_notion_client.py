"""Tests for NotionClient (M5, Task-003).

Offline tests: the pure ``build_page`` mapping and ``from_env`` config loading
are exercised directly; the network ``create_page`` call is stubbed via
``urllib.request.urlopen`` to verify the returned page id.
"""

from __future__ import annotations

import io
from typing import NoReturn, Self
from urllib.error import HTTPError, URLError

import pytest

from arkmind.notion import MissingNotionConfigError, NotionClient, NotionEnvironmentError


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


def test_verify_token_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    client = NotionClient(token="secret", database_id="db123")

    monkeypatch.setattr("urllib.request.urlopen", lambda _request: _FakeResponse(b"{}"))

    client.verify_token()  # no exception


def test_verify_token_rejects_invalid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    client = NotionClient(token="secret", database_id="db123")

    def _raise_401(_request: object) -> NoReturn:
        raise HTTPError("url", 401, "Unauthorized", {}, io.BytesIO(b"{}"))

    monkeypatch.setattr("urllib.request.urlopen", _raise_401)

    with pytest.raises(NotionEnvironmentError, match="Token is invalid or revoked"):
        client.verify_token()


def test_verify_token_network_error(monkeypatch: pytest.MonkeyPatch) -> None:
    client = NotionClient(token="secret", database_id="db123")

    def _raise_net(_request: object) -> NoReturn:
        raise URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", _raise_net)

    with pytest.raises(NotionEnvironmentError, match="Network error"):
        client.verify_token()


def test_verify_database_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    client = NotionClient(token="secret", database_id="db123")

    monkeypatch.setattr("urllib.request.urlopen", lambda _request: _FakeResponse(b"{}"))

    client.verify_database()  # no exception


def test_verify_database_not_shared(monkeypatch: pytest.MonkeyPatch) -> None:
    client = NotionClient(token="secret", database_id="db123")

    def _raise_404(_request: object) -> NoReturn:
        raise HTTPError("url", 404, "Not Found", {}, io.BytesIO(b"{}"))

    monkeypatch.setattr("urllib.request.urlopen", _raise_404)

    with pytest.raises(NotionEnvironmentError, match="Database not found") as excinfo:
        client.verify_database()
    assert "Share → invite" in str(excinfo.value)


def test_verify_database_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    client = NotionClient(token="secret", database_id="db123")

    def _raise_403(_request: object) -> NoReturn:
        raise HTTPError("url", 403, "Forbidden", {}, io.BytesIO(b"{}"))

    monkeypatch.setattr("urllib.request.urlopen", _raise_403)

    with pytest.raises(NotionEnvironmentError, match="Access denied"):
        client.verify_database()
