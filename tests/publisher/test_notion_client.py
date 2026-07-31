"""Tests for the NotionClient mapping and config (M5 Publisher, Task-001).

These are offline tests: only the pure ``build_page`` mapping and ``from_env``
config loading are exercised. The network ``publish`` call is never invoked.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from arkmind.publisher import Article, ArticleMetadata, MissingNotionConfigError, NotionClient


def _article(content: str = "Body", *, book: str = "The Black Swan") -> Article:
    return Article(
        id="a1",
        title="On Randomness",
        content=content,
        metadata=ArticleMetadata(
            book=book,
            author="ArkMind",
            created_at=datetime(2026, 7, 31, 12, 0, 0, tzinfo=UTC),
            word_count=1200,
            topic_count=3,
            asset_count=8,
        ),
    )


def test_build_page_maps_all_frozen_fields() -> None:
    client = NotionClient(token="secret", database_id="db123")

    page = client.build_page(_article())

    assert page["parent"] == {"database_id": "db123"}
    props = page["properties"]
    assert isinstance(props, dict)
    assert props["Title"] == {"title": [{"text": {"content": "On Randomness"}}]}
    assert props["Content"] == {"rich_text": [{"text": {"content": "Body"}}]}
    assert props["Book"] == {"rich_text": [{"text": {"content": "The Black Swan"}}]}
    assert props["Author"] == {"rich_text": [{"text": {"content": "ArkMind"}}]}
    assert props["Created Time"] == {"date": {"start": "2026-07-31T12:00:00+00:00"}}
    assert props["Word Count"] == {"number": 1200}
    assert props["Topic Count"] == {"number": 3}
    assert props["Asset Count"] == {"number": 8}


def test_build_page_chunks_content_over_rich_text_limit() -> None:
    client = NotionClient(token="secret", database_id="db123")
    long_content = "x" * 4500  # 2000 + 2000 + 500

    page = client.build_page(_article(content=long_content))

    chunks = page["properties"]["Content"]["rich_text"]  # type: ignore[index]
    lengths = [len(chunk["text"]["content"]) for chunk in chunks]
    assert lengths == [2000, 2000, 500]
    assert "".join(chunk["text"]["content"] for chunk in chunks) == long_content


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

    assert client.build_page(_article())["parent"] == {"database_id": "db123"}
