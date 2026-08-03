"""Tests for NotionClient (M5, Task-003; Editorial Database v2).

Offline tests: the pure ``build_page`` mapping and ``from_env`` config loading
are exercised directly; the network calls (``create_page`` / ``fetch_page`` /
``fetch_children``) are stubbed via ``urllib.request.urlopen``.
"""

from __future__ import annotations

import io
from typing import NoReturn, Self
from urllib.error import HTTPError, URLError

import pytest

from arkmind.notion import MissingNotionConfigError, NotionClient, NotionEnvironmentError
from arkmind.notion.notion_client import word_count


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


def test_build_page_maps_management_properties() -> None:
    client = NotionClient(token="secret", database_id="db123")

    page = client.build_page("On Randomness", "Body", book="黑天鹅", author="塔勒布")

    assert page["parent"] == {"database_id": "db123"}
    props = page["properties"]
    assert isinstance(props, dict)
    assert props["Title"] == {"title": [{"text": {"content": "On Randomness"}}]}
    assert props["Book"] == {"rich_text": [{"text": {"content": "黑天鹅"}}]}
    assert props["Author"] == {"rich_text": [{"text": {"content": "塔勒布"}}]}
    assert props["Status"] == {"select": {"name": "Draft"}}
    assert props["Word Count"] == {"number": 4}  # "Body"


def test_build_page_omits_empty_book_and_author() -> None:
    client = NotionClient(token="secret", database_id="db123")

    page = client.build_page("T", "Body")

    props = page["properties"]
    assert isinstance(props, dict)
    assert props["Book"] == {"rich_text": []}
    assert props["Author"] == {"rich_text": []}


def test_build_page_never_writes_content_property() -> None:
    client = NotionClient(token="secret", database_id="db123")

    page = client.build_page("T", "Body")

    assert "Content" not in page["properties"]  # type: ignore[operator]


def test_build_page_body_starts_with_content_and_ends_with_footer() -> None:
    client = NotionClient(token="secret", database_id="db123")

    children = client.build_page("T", "正文\n\n第二段")["children"]
    assert isinstance(children, list)

    # Body template: content first (its level-1 heading is the article title),
    # then the Editor Notes / Review footer.
    types = [child["type"] for child in children]
    assert types == [
        "paragraph",
        "paragraph",
        "divider",
        "heading_2",
        "divider",
        "heading_2",
    ]
    assert children[0]["paragraph"]["rich_text"][0]["text"]["content"] == "正文"  # type: ignore[index]
    assert children[3]["heading_2"]["rich_text"][0]["text"]["content"] == "Editor Notes"  # type: ignore[index]
    assert children[5]["heading_2"]["rich_text"][0]["text"]["content"] == "Review"  # type: ignore[index]


def test_build_page_long_paragraph_chunked_in_blocks() -> None:
    client = NotionClient(token="secret", database_id="db123")
    long_content = "x" * 4500  # 2000 + 2000 + 500

    page = client.build_page("T", long_content)

    children = page["children"]
    assert isinstance(children, list)
    spans = children[0]["paragraph"]["rich_text"]  # type: ignore[index]
    lengths = [len(span["text"]["content"]) for span in spans]
    assert lengths == [2000, 2000, 500]
    assert "".join(span["text"]["content"] for span in spans) == long_content


def test_word_count_strips_whitespace() -> None:
    assert word_count("a b\nc") == 3
    assert word_count("") == 0


def test_create_page_returns_page_id(monkeypatch: pytest.MonkeyPatch) -> None:
    client = NotionClient(token="secret", database_id="db123")

    def _fake_urlopen(_request: object) -> _FakeResponse:
        return _FakeResponse(b'{"id":"page_123","object":"page"}')

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

    assert client.create_page("On Randomness", "Body") == "page_123"


def test_fetch_page_returns_raw_page(monkeypatch: pytest.MonkeyPatch) -> None:
    client = NotionClient(token="secret", database_id="db123")

    def _fake_urlopen(_request: object) -> _FakeResponse:
        return _FakeResponse(b'{"id":"page_123","properties":{}}')

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

    assert client.fetch_page("page_123")["id"] == "page_123"


def test_fetch_children_returns_blocks(monkeypatch: pytest.MonkeyPatch) -> None:
    client = NotionClient(token="secret", database_id="db123")

    def _fake_urlopen(_request: object) -> _FakeResponse:
        return _FakeResponse(b'{"results":[{"type":"heading_1"}]}')

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

    assert client.fetch_children("page_123") == [{"type": "heading_1"}]


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
