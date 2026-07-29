"""Tests for KnowledgeReferenceDetector (RFC-0013)."""

from __future__ import annotations

from arkmind.knowledge.models import Knowledge
from arkmind.knowledge.reference import KnowledgeReference, KnowledgeReferenceDetector


def _knowledge(knowledge_id: str, text: str) -> Knowledge:
    return Knowledge(
        knowledge_id=knowledge_id,
        fragment_id=f"f-{knowledge_id}",
        source_id="dataset-0001",
        text=text,
    )


def test_no_function() -> None:
    result = KnowledgeReferenceDetector().detect([_knowledge("k1", "a plain sentence")])
    assert result == []


def test_single_function() -> None:
    result = KnowledgeReferenceDetector().detect([_knowledge("k1", "use ST_Area here")])
    assert result == [
        KnowledgeReference(source_id="dataset-0001", from_knowledge_id="k1", to_function="ST_Area")
    ]


def test_multiple_functions() -> None:
    result = KnowledgeReferenceDetector().detect(
        [_knowledge("k1", "ST_Contains wraps ST_Intersects")]
    )
    assert [r.to_function for r in result] == ["ST_Contains", "ST_Intersects"]


def test_duplicate_references_preserved() -> None:
    result = KnowledgeReferenceDetector().detect([_knowledge("k1", "ST_Area then ST_Area")])
    assert [r.to_function for r in result] == ["ST_Area", "ST_Area"]


def test_multiple_knowledge() -> None:
    result = KnowledgeReferenceDetector().detect(
        [_knowledge("k1", "ST_Area"), _knowledge("k2", "ST_Length")]
    )
    assert [(r.from_knowledge_id, r.to_function) for r in result] == [
        ("k1", "ST_Area"),
        ("k2", "ST_Length"),
    ]


def test_order_is_stable() -> None:
    result = KnowledgeReferenceDetector().detect(
        [_knowledge("k1", "ST_B and ST_A"), _knowledge("k2", "ST_C")]
    )
    assert [(r.from_knowledge_id, r.to_function) for r in result] == [
        ("k1", "ST_B"),
        ("k1", "ST_A"),
        ("k2", "ST_C"),
    ]


def test_only_st_prefix_matches() -> None:
    result = KnowledgeReferenceDetector().detect(
        [_knowledge("k1", "postgis_ST_Area and GeomFromText and ST_Union")]
    )
    assert [r.to_function for r in result] == ["ST_Union"]
