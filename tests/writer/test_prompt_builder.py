"""Tests for the Writer PromptBuilder (M3 Task-002).

Cover empty / single / multi Topic, correct prompt loading (externalised
writer.md), and loss-less Context assembly (concept/definition/quote content
present verbatim). The prompt is loaded from a temp dir so tests are hermetic.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from arkmind.asset import Asset, AssetRepository, AssetType
from arkmind.runtime import PromptLoader
from arkmind.topic import Topic
from arkmind.writer import PromptBuilder

_INSTRUCTION = "写一篇原创博文的指令占位。"


@pytest.fixture
def loader(tmp_path: Path) -> PromptLoader:
    (tmp_path / "writer.md").write_text(_INSTRUCTION, encoding="utf-8")
    return PromptLoader(tmp_path)


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


def test_build_empty_topics_loads_instruction_only(loader: PromptLoader) -> None:
    prompt = PromptBuilder(loader=loader).build([], AssetRepository())

    assert _INSTRUCTION in prompt


def test_build_single_topic_includes_all_content(loader: PromptLoader) -> None:
    repo = _repo(
        _asset("c1", AssetType.CONCEPT, "概念正文A"),
        _asset("d1", AssetType.DEFINITION, "定义正文B"),
        _asset("q1", AssetType.QUOTE, "引文正文C"),
    )
    topic = Topic(
        topic_id="topic-001",
        title="黑天鹅",
        concepts=["c1"],
        definitions=["d1"],
        quotes=["q1"],
    )

    prompt = PromptBuilder(loader=loader).build([topic], repo)

    assert _INSTRUCTION in prompt
    assert "黑天鹅" in prompt
    assert "概念正文A" in prompt
    assert "定义正文B" in prompt
    assert "引文正文C" in prompt


def test_build_multi_topic_includes_every_topic(loader: PromptLoader) -> None:
    repo = _repo(
        _asset("c1", AssetType.CONCEPT, "内容1"),
        _asset("c2", AssetType.CONCEPT, "内容2"),
    )
    topics = [
        Topic(topic_id="topic-001", title="主题甲", concepts=["c1"], definitions=[], quotes=[]),
        Topic(topic_id="topic-002", title="主题乙", concepts=["c2"], definitions=[], quotes=[]),
    ]

    prompt = PromptBuilder(loader=loader).build(topics, repo)

    assert "主题甲" in prompt
    assert "主题乙" in prompt
    assert "内容1" in prompt
    assert "内容2" in prompt


def test_build_marks_empty_sections(loader: PromptLoader) -> None:
    topic = Topic(topic_id="topic-001", title="空主题", concepts=[], definitions=[], quotes=[])

    prompt = PromptBuilder(loader=loader).build([topic], AssetRepository())

    assert "空主题" in prompt
    assert "（无）" in prompt
