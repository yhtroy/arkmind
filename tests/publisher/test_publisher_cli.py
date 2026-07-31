"""Tests for the Publisher CLI (M5 Publisher, Task-001).

Offline: the destination client is replaced with a recording fake, so the CLI is
exercised end-to-end (JSON in -> publish -> "Published") without touching Notion.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from arkmind.publisher import Article, ArticleMetadata, PublisherClient, publisher_cli


class _RecordingClient(PublisherClient):
    def __init__(self) -> None:
        self.published: list[Article] = []

    def publish(self, article: Article) -> None:
        self.published.append(article)


def _write_article_json(path: Path) -> Article:
    article = Article(
        id="a1",
        title="On Randomness",
        content="Body",
        metadata=ArticleMetadata(
            book="The Black Swan",
            author="ArkMind",
            created_at=datetime(2026, 7, 31, 12, 0, 0, tzinfo=UTC),
            word_count=1200,
            topic_count=3,
            asset_count=8,
        ),
    )
    path.write_text(article.model_dump_json(), encoding="utf-8")
    return article


def test_main_reads_article_and_publishes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    article_path = tmp_path / "article.json"
    expected = _write_article_json(article_path)

    client = _RecordingClient()
    monkeypatch.setattr(publisher_cli, "_build_client", lambda: client)
    monkeypatch.setattr("sys.argv", ["arkmind-publisher", str(article_path)])

    publisher_cli.main()

    assert client.published == [expected]
    assert capsys.readouterr().out.strip() == "Published"
