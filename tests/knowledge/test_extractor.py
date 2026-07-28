"""Tests for KnowledgeExtractor (RFC-0004)."""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from arkmind.fragment.models import Fragment
from arkmind.knowledge.extractor import KnowledgeExtractor
from arkmind.knowledge.models import Knowledge


def _fragment(fragment_id: str, sequence: int, text: str) -> Fragment:
    return Fragment(fragment_id=fragment_id, page_number=1, sequence=sequence, text=text)


_SOURCE_ID = "dataset-0001"


def _expected_id(fragment_id: str, text: str) -> str:
    payload = f"{fragment_id}\n{text}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_empty_input_returns_empty_list() -> None:
    assert KnowledgeExtractor().extract([], _SOURCE_ID) == []


def test_single_fragment_maps_to_single_knowledge() -> None:
    result = KnowledgeExtractor().extract([_fragment("frag-1", 0, "Hello")], _SOURCE_ID)
    assert len(result) == 1
    knowledge = result[0]
    assert isinstance(knowledge, Knowledge)
    assert knowledge.fragment_id == "frag-1"
    assert knowledge.text == "Hello"
    assert knowledge.knowledge_id == _expected_id("frag-1", "Hello")


def test_source_id_is_written_to_every_knowledge() -> None:
    fragments = [_fragment("a", 0, "A"), _fragment("b", 1, "B")]
    result = KnowledgeExtractor().extract(fragments, _SOURCE_ID)
    assert [k.source_id for k in result] == [_SOURCE_ID, _SOURCE_ID]


def test_multiple_fragments_preserve_order() -> None:
    fragments = [_fragment("a", 0, "A"), _fragment("b", 1, "B"), _fragment("c", 2, "C")]
    result = KnowledgeExtractor().extract(fragments, _SOURCE_ID)
    assert [(k.fragment_id, k.text) for k in result] == [("a", "A"), ("b", "B"), ("c", "C")]


def test_knowledge_id_is_stable_and_matches_algorithm() -> None:
    fragments = [_fragment("frag-1", 0, "Alpha"), _fragment("frag-2", 1, "Beta")]
    first = KnowledgeExtractor().extract(fragments, _SOURCE_ID)
    second = KnowledgeExtractor().extract(fragments, _SOURCE_ID)
    assert [k.knowledge_id for k in first] == [k.knowledge_id for k in second]
    assert first[0].knowledge_id == _expected_id("frag-1", "Alpha")
    assert first[1].knowledge_id == _expected_id("frag-2", "Beta")


def test_extra_field_is_forbidden() -> None:
    with pytest.raises(ValidationError):
        Knowledge(knowledge_id="k", fragment_id="f", source_id="s", text="t", extra_field="nope")
