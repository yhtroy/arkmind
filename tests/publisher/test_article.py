"""Tests for the Article data model (M5 Publisher, Task-001)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from arkmind.publisher import Article, ArticleMetadata


def _metadata() -> ArticleMetadata:
    return ArticleMetadata(
        book="The Black Swan",
        author="ArkMind",
        created_at=datetime(2026, 7, 31, 12, 0, 0, tzinfo=UTC),
        word_count=1200,
        topic_count=3,
        asset_count=8,
    )


def test_article_round_trips_through_json() -> None:
    article = Article(id="a1", title="Title", content="Body", metadata=_metadata())
    restored = Article.model_validate_json(article.model_dump_json())
    assert restored == article


def test_article_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Article(
            id="a1",
            title="Title",
            content="Body",
            metadata=_metadata(),
            extra="nope",  # type: ignore[call-arg]
        )


def test_metadata_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ArticleMetadata(
            book="b",
            author="a",
            created_at=datetime(2026, 7, 31, tzinfo=UTC),
            word_count=1,
            topic_count=1,
            asset_count=1,
            tags=["x"],  # type: ignore[call-arg]
        )
