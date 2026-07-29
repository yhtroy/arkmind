"""Tests for KnowledgeNormalizer (RFC-0011)."""

from __future__ import annotations

from arkmind.knowledge.models import Knowledge
from arkmind.knowledge.normalizer import KnowledgeNormalizer


def _knowledge(text: str) -> Knowledge:
    return Knowledge(
        knowledge_id="k1",
        fragment_id="f1",
        source_id="dataset-0001",
        text=text,
    )


def _normalize_one(text: str) -> str:
    result = KnowledgeNormalizer().normalize([_knowledge(text)])
    assert result[0].normalized is not None
    return result[0].normalized


def test_rfc_example() -> None:
    assert _normalize_one("A geometry may be empty.") == "A geometry may be empty"


def test_trim() -> None:
    assert _normalize_one("   hello world   ") == "hello world"


def test_collapse_whitespace() -> None:
    assert _normalize_one("a\t b\n\nc   d") == "a b c d"


def test_strip_single_trailing_dot() -> None:
    assert _normalize_one("done.") == "done"
    assert _normalize_one("wait..") == "wait."


def test_preserve_case() -> None:
    assert _normalize_one("PostGIS Supports Geometry") == "PostGIS Supports Geometry"


def test_strip_markdown_bold_italic_and_code() -> None:
    assert _normalize_one("a **bold** and *italic* and `code` word") == (
        "a bold and italic and code word"
    )


def test_strip_leading_heading_and_quote() -> None:
    assert _normalize_one("# Title here") == "Title here"
    assert _normalize_one("> quoted text") == "quoted text"


def test_preserve_all_words_and_code_tokens() -> None:
    # Identifiers, SQL wildcards and function signatures must survive untouched.
    assert _normalize_one("ST_Area(geom) uses postgis_tiger_geocoder") == (
        "ST_Area(geom) uses postgis_tiger_geocoder"
    )
    assert _normalize_one("SELECT * FROM roads") == "SELECT * FROM roads"


def test_original_text_not_modified() -> None:
    original = _knowledge("  raw **text**.  ")
    KnowledgeNormalizer().normalize([original])
    assert original.text == "  raw **text**.  "
    assert original.normalized is None


def test_returns_new_list_with_normalized_set() -> None:
    items = [_knowledge("one two."), _knowledge("three")]
    result = KnowledgeNormalizer().normalize(items)
    assert [k.normalized for k in result] == ["one two", "three"]
    assert [k.text for k in result] == ["one two.", "three"]


def test_empty_input() -> None:
    assert KnowledgeNormalizer().normalize([]) == []
