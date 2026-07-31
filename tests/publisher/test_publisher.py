"""Tests for the Publisher adapter (M5 Publisher, Task-001)."""

from __future__ import annotations

from datetime import UTC, datetime

from arkmind.publisher import Article, ArticleMetadata, Publisher, PublisherClient


class _RecordingClient(PublisherClient):
    def __init__(self) -> None:
        self.published: list[Article] = []

    def publish(self, article: Article) -> None:
        self.published.append(article)


def _article() -> Article:
    return Article(
        id="a1",
        title="Title",
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


def test_publisher_delegates_to_client_unchanged() -> None:
    client = _RecordingClient()
    article = _article()

    Publisher(client).publish(article)

    assert client.published == [article]
    # The Publisher must not mutate the article on the way through.
    assert client.published[0] is article
