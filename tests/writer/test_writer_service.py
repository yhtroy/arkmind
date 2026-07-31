"""Tests for the WriterService skeleton (M3 Writer, Task-001)."""

from __future__ import annotations

from arkmind.topic import Topic
from arkmind.writer import WriterService


def _topic(topic_id: str, title: str) -> Topic:
    return Topic(topic_id=topic_id, title=title, concepts=[], definitions=[], quotes=[])


def test_write_lists_topic_titles() -> None:
    topics = [_topic("topic-001", "黑天鹅"), _topic("topic-002", "极端斯坦")]

    article = WriterService().write(topics)

    assert "黑天鹅" in article.body
    assert "极端斯坦" in article.body
    assert "共 2 个 Topic" in article.body
    assert article.title


def test_write_is_deterministic() -> None:
    topics = [_topic("topic-001", "黑天鹅")]

    first = WriterService().write(topics)
    second = WriterService().write(topics)

    assert first == second


def test_write_handles_empty_topics() -> None:
    article = WriterService().write([])

    assert "共 0 个 Topic" in article.body
    assert article.title
