"""Tests for the AssetResolver (M3 Task-002).

Verify that a Topic's asset_id references are expanded to full Asset content,
that Topic stays reference-only, and that dangling references are skipped.
"""

from __future__ import annotations

from datetime import UTC, datetime

from arkmind.asset import Asset, AssetRepository, AssetType
from arkmind.topic import Topic
from arkmind.writer import AssetResolver


def _asset(asset_id: str, asset_type: AssetType, content: str) -> Asset:
    return Asset(
        asset_id=asset_id,
        book_id="b1",
        knowledge_id="k1",
        type=asset_type,
        content=content,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _repo(*assets: Asset) -> AssetRepository:
    repo = AssetRepository()
    for asset in assets:
        repo.add(asset)
    return repo


def test_resolve_expands_references_to_content() -> None:
    repo = _repo(
        _asset("c1", AssetType.CONCEPT, "Concept:\n黑天鹅\nDescription:\nd"),
        _asset("d1", AssetType.DEFINITION, "Term:\n黑天鹅\nDefinition:\ndef"),
        _asset("q1", AssetType.QUOTE, "一句引文"),
    )
    topic = Topic(
        topic_id="topic-001",
        title="黑天鹅",
        concepts=["c1"],
        definitions=["d1"],
        quotes=["q1"],
    )

    resolved = AssetResolver().resolve(topic, repo)

    assert resolved.title == "黑天鹅"
    assert resolved.concepts == ["Concept:\n黑天鹅\nDescription:\nd"]
    assert resolved.definitions == ["Term:\n黑天鹅\nDefinition:\ndef"]
    assert resolved.quotes == ["一句引文"]


def test_resolve_skips_dangling_reference() -> None:
    repo = _repo(_asset("c1", AssetType.CONCEPT, "存在"))
    topic = Topic(
        topic_id="topic-001",
        title="t",
        concepts=["c1", "missing"],
        definitions=[],
        quotes=[],
    )

    resolved = AssetResolver().resolve(topic, repo)

    assert resolved.concepts == ["存在"]


def test_resolve_handles_empty_topic() -> None:
    topic = Topic(topic_id="topic-001", title="t", concepts=[], definitions=[], quotes=[])

    resolved = AssetResolver().resolve(topic, AssetRepository())

    assert resolved.concepts == []
    assert resolved.definitions == []
    assert resolved.quotes == []
