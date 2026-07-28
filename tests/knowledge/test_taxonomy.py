"""Tests for KnowledgeTaxonomy (RFC-0005)."""

from __future__ import annotations

from arkmind.knowledge.models import Knowledge
from arkmind.knowledge.taxonomy import KnowledgeTaxonomy


def _knowledge(text: str) -> Knowledge:
    return Knowledge(knowledge_id="k", fragment_id="f", source_id="s", text=text)


def _classify_one(text: str) -> str | None:
    result = KnowledgeTaxonomy().classify([_knowledge(text)])
    return result[0].kind


def test_constraint() -> None:
    assert _classify_one("This step must be completed") == "constraint"


def test_warning() -> None:
    assert _classify_one("Warning: high voltage") == "warning"


def test_example() -> None:
    assert _classify_one("For example, consider a tree") == "example"


def test_definition() -> None:
    assert _classify_one("A vector is defined as an ordered tuple") == "definition"


def test_reference() -> None:
    assert _classify_one("See appendix B for details") == "reference"


def test_quote() -> None:
    assert _classify_one('"knowledge is power"') == "quote"


def test_unknown() -> None:
    assert _classify_one("A plain sentence about nothing") == "unknown"


def test_priority_first_matching_rule_wins() -> None:
    # Contains constraint, warning, example and reference keywords at once;
    # constraint (Rule 1) must win.
    assert _classify_one("You must see this warning example") == "constraint"


def test_case_insensitive() -> None:
    assert _classify_one("MUST comply with the policy") == "constraint"


def test_empty_input_returns_empty_list() -> None:
    assert KnowledgeTaxonomy().classify([]) == []


def test_order_and_other_fields_preserved() -> None:
    items = [_knowledge("must do"), _knowledge("plain")]
    original_ids = [k.knowledge_id for k in items]
    result = KnowledgeTaxonomy().classify(items)
    assert [k.knowledge_id for k in result] == original_ids
    assert [k.kind for k in result] == ["constraint", "unknown"]
    assert [k.text for k in result] == ["must do", "plain"]
