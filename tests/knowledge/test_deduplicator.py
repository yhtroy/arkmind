"""Tests for KnowledgeDeduplicator (RFC-0012)."""

from __future__ import annotations

from arkmind.knowledge.deduplicator import KnowledgeDeduplicator
from arkmind.knowledge.models import Knowledge


def _knowledge(knowledge_id: str, normalized: str) -> Knowledge:
    return Knowledge(
        knowledge_id=knowledge_id,
        fragment_id=f"f-{knowledge_id}",
        source_id="dataset-0001",
        text=f"{normalized}.",
        kind="reference",
        normalized=normalized,
    )


def test_empty_input() -> None:
    assert KnowledgeDeduplicator().deduplicate([]) == []


def test_no_duplicates() -> None:
    items = [_knowledge("k1", "alpha"), _knowledge("k2", "beta"), _knowledge("k3", "gamma")]
    result = KnowledgeDeduplicator().deduplicate(items)
    assert [k.duplicate for k in result] == [False, False, False]


def test_two_duplicates() -> None:
    items = [_knowledge("k1", "same"), _knowledge("k2", "same")]
    result = KnowledgeDeduplicator().deduplicate(items)
    assert [k.duplicate for k in result] == [False, True]


def test_many_duplicates() -> None:
    items = [
        _knowledge("k1", "a"),
        _knowledge("k2", "b"),
        _knowledge("k3", "a"),
        _knowledge("k4", "a"),
        _knowledge("k5", "b"),
    ]
    result = KnowledgeDeduplicator().deduplicate(items)
    assert [k.duplicate for k in result] == [False, False, True, True, True]


def test_order_preserved() -> None:
    items = [_knowledge("k1", "x"), _knowledge("k2", "y"), _knowledge("k3", "x")]
    result = KnowledgeDeduplicator().deduplicate(items)
    assert [k.knowledge_id for k in result] == ["k1", "k2", "k3"]


def test_duplicate_flag_marks_first_false_rest_true() -> None:
    items = [_knowledge("k1", "dup"), _knowledge("k2", "dup"), _knowledge("k3", "dup")]
    result = KnowledgeDeduplicator().deduplicate(items)
    assert result[0].duplicate is False
    assert result[1].duplicate is True
    assert result[2].duplicate is True


def test_other_fields_not_modified() -> None:
    items = [_knowledge("k1", "dup"), _knowledge("k2", "dup")]
    result = KnowledgeDeduplicator().deduplicate(items)
    for original, marked in zip(items, result):
        assert marked.knowledge_id == original.knowledge_id
        assert marked.fragment_id == original.fragment_id
        assert marked.source_id == original.source_id
        assert marked.kind == original.kind
        assert marked.text == original.text
        assert marked.normalized == original.normalized
    # input list is not mutated
    assert all(item.duplicate is False for item in items)
