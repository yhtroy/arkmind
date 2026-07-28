"""Tests for ProvenanceBuilder (RFC-0006)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from arkmind.knowledge.models import Knowledge
from arkmind.provenance.builder import ProvenanceBuilder
from arkmind.provenance.models import Provenance


def _knowledge(knowledge_id: str, fragment_id: str, source_id: str) -> Knowledge:
    return Knowledge(
        knowledge_id=knowledge_id,
        fragment_id=fragment_id,
        source_id=source_id,
        text="text",
    )


def test_empty_input_returns_empty_list() -> None:
    assert ProvenanceBuilder().build([]) == []


def test_single_knowledge() -> None:
    result = ProvenanceBuilder().build([_knowledge("k1", "f1", "s1")])
    assert len(result) == 1
    assert isinstance(result[0], Provenance)


def test_multiple_knowledge() -> None:
    items = [_knowledge("k1", "f1", "s1"), _knowledge("k2", "f2", "s1")]
    result = ProvenanceBuilder().build(items)
    assert len(result) == 2


def test_order_preserved() -> None:
    items = [
        _knowledge("k1", "f1", "s1"),
        _knowledge("k2", "f2", "s1"),
        _knowledge("k3", "f3", "s2"),
    ]
    result = ProvenanceBuilder().build(items)
    assert [p.knowledge_id for p in result] == ["k1", "k2", "k3"]


def test_field_mapping_is_verbatim() -> None:
    result = ProvenanceBuilder().build([_knowledge("kid", "fid", "sid")])
    assert (result[0].knowledge_id, result[0].fragment_id, result[0].source_id) == (
        "kid",
        "fid",
        "sid",
    )


def test_source_id_is_copied_from_knowledge() -> None:
    result = ProvenanceBuilder().build([_knowledge("k", "f", "dataset-0001")])
    assert result[0].source_id == "dataset-0001"


def test_extra_field_is_forbidden() -> None:
    with pytest.raises(ValidationError):
        Provenance(knowledge_id="k", fragment_id="f", source_id="s", extra_field="nope")
