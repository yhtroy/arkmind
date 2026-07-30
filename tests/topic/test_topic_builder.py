"""Tests for TopicBuilder (RFC-M2.2-001, Topic Builder MVP).

Cover the frozen deterministic rules: exact-name grouping across Concept /
Definition, Definition-only Topics, Quote substring attachment (multi + drop),
None skipping and deterministic id ordering.
"""

from __future__ import annotations

from datetime import UTC, datetime

from arkmind.asset import Asset, AssetType
from arkmind.topic import TopicBuilder


def _asset(asset_type: AssetType, content: str, asset_id: str) -> Asset:
    return Asset(
        asset_id=asset_id,
        book_id="b1",
        knowledge_id="k1",
        type=asset_type,
        content=content,
        created_at=datetime.now(UTC),
    )


def _concept(name: str, asset_id: str) -> Asset:
    return _asset(
        AssetType.CONCEPT, f"Concept:\n{name}\nDescription:\nd\nSignificance:\ns", asset_id
    )


def _definition(term: str, asset_id: str) -> Asset:
    return _asset(AssetType.DEFINITION, f"Term:\n{term}\nDefinition:\nd\nBoundary:\nb", asset_id)


def _quote(text: str, asset_id: str) -> Asset:
    return _asset(AssetType.QUOTE, text, asset_id)


def test_same_concept_name_merges_into_one_topic() -> None:
    topics = TopicBuilder().build([_concept("极端斯坦", "a1"), _concept("极端斯坦", "a2")])

    assert len(topics) == 1
    assert topics[0].title == "极端斯坦"
    assert topics[0].concepts == ["a1", "a2"]


def test_definition_term_shares_namespace_with_concept_name() -> None:
    topics = TopicBuilder().build([_concept("黑天鹅", "a1"), _definition("黑天鹅", "a2")])

    assert len(topics) == 1
    assert topics[0].concepts == ["a1"]
    assert topics[0].definitions == ["a2"]


def test_definition_only_term_forms_its_own_topic() -> None:
    topics = TopicBuilder().build([_definition("叙述谬误", "a1")])

    assert len(topics) == 1
    assert topics[0].title == "叙述谬误"
    assert topics[0].concepts == []
    assert topics[0].definitions == ["a1"]


def test_quote_attaches_to_every_matching_topic_and_drops_unmatched() -> None:
    topics = TopicBuilder().build(
        [
            _concept("极端斯坦", "a1"),
            _concept("黑天鹅", "a2"),
            _quote("极端斯坦 与 黑天鹅 密切相关", "q1"),
            _quote("一句无关的话", "q2"),
        ]
    )

    by_title = {t.title: t for t in topics}
    assert by_title["极端斯坦"].quotes == ["q1"]
    assert by_title["黑天鹅"].quotes == ["q1"]
    assert all("q2" not in t.quotes for t in topics)


def test_none_content_is_skipped() -> None:
    topics = TopicBuilder().build(
        [_concept("极端斯坦", "a1"), _asset(AssetType.CONCEPT, "None", "a2")]
    )

    assert len(topics) == 1
    assert topics[0].concepts == ["a1"]


def test_topics_are_ordered_by_size_then_title_with_sequential_ids() -> None:
    topics = TopicBuilder().build(
        [
            _concept("B", "b1"),
            _concept("A", "a1"),
            _concept("A", "a2"),
        ]
    )

    assert [(t.topic_id, t.title) for t in topics] == [
        ("topic-001", "A"),
        ("topic-002", "B"),
    ]
