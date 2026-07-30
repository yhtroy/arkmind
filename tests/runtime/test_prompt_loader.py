"""Tests for PromptLoader (Runtime Contract v1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from arkmind.runtime import PromptLoader, PromptNotFoundError


def test_loads_prompt_by_category_and_name(tmp_path: Path) -> None:
    (tmp_path / "asset").mkdir()
    (tmp_path / "asset" / "concept.md").write_text("extract concepts", encoding="utf-8")
    assert PromptLoader(root=tmp_path).load("asset/concept") == "extract concepts"


def test_missing_prompt_raises(tmp_path: Path) -> None:
    with pytest.raises(PromptNotFoundError):
        PromptLoader(root=tmp_path).load("asset/nope")
