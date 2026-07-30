"""Tests for AssetExtractor (Asset Contract v1, TASK-004)."""

from __future__ import annotations

from pathlib import Path

from arkmind.asset import AssetExtractor, AssetType
from arkmind.knowledge.models import Knowledge
from arkmind.runtime import FakeLLMClient, PromptLoader


def _loader(root: Path) -> PromptLoader:
    asset_dir = root / "asset"
    asset_dir.mkdir()
    for name in ("concept", "definition", "quote"):
        (asset_dir / f"{name}.md").write_text(f"{name} prompt", encoding="utf-8")
    return PromptLoader(root=root)


def _knowledge(knowledge_id: str = "k1") -> Knowledge:
    return Knowledge(
        knowledge_id=knowledge_id,
        fragment_id="f1",
        source_id="book-1",
        text="long-term thinking compounds",
    )


def test_one_knowledge_yields_three_typed_assets(tmp_path: Path) -> None:
    extractor = AssetExtractor(loader=_loader(tmp_path), llm=FakeLLMClient(response="X"))
    assets = extractor.extract([_knowledge()])
    assert [a.type for a in assets] == [
        AssetType.CONCEPT,
        AssetType.DEFINITION,
        AssetType.QUOTE,
    ]
    assert all(a.book_id == "book-1" for a in assets)
    assert all(a.knowledge_id == "k1" for a in assets)


def test_content_is_verbatim_response(tmp_path: Path) -> None:
    extractor = AssetExtractor(loader=_loader(tmp_path), llm=FakeLLMClient(response="verbatim"))
    assets = extractor.extract([_knowledge()])
    assert all(a.content == "verbatim" for a in assets)


def test_blank_response_produces_no_asset(tmp_path: Path) -> None:
    extractor = AssetExtractor(loader=_loader(tmp_path), llm=FakeLLMClient(response="   "))
    assert extractor.extract([_knowledge()]) == []


def test_asset_ids_are_unique(tmp_path: Path) -> None:
    extractor = AssetExtractor(loader=_loader(tmp_path), llm=FakeLLMClient(response="X"))
    assets = extractor.extract([_knowledge("k1"), _knowledge("k2")])
    assert len({a.asset_id for a in assets}) == 6


def test_empty_knowledge_list_yields_no_assets(tmp_path: Path) -> None:
    extractor = AssetExtractor(loader=_loader(tmp_path), llm=FakeLLMClient(response="X"))
    assert extractor.extract([]) == []
