"""Tests for the arkmind-writer CLI (M3 Writer, M5 Task-003).

Exercise the chain: read topic.json + asset.json -> WriterService (offline
clients) -> Notion page id, plus the empty-input edge case. No network or API
key.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arkmind.runtime import FakeLLMClient, OpenAICompatibleClient
from arkmind.writer import writer_cli
from arkmind.writer.writer_cli import _build_llm


class _CannedLLM:
    """Offline stand-in for FakeLLMClient returning an H1-bearing response."""

    def generate(self, prompt: str, text: str) -> str:
        return "# 黑天鹅\n\n极不可能却影响巨大的事件"


class _RecordingNotion:
    """Offline stand-in for NotionClient — records without any network."""

    def __init__(self) -> None:
        self.stored: list[tuple[str, str]] = []

    def create_page(self, title: str, content: str) -> str:
        self.stored.append((title, content))
        return "page_001"


def _topic(topic_id: str, title: str, concepts: list[str]) -> dict[str, object]:
    return {
        "topic_id": topic_id,
        "title": title,
        "concepts": concepts,
        "definitions": [],
        "quotes": [],
    }


def _asset(asset_id: str, content: str) -> dict[str, object]:
    return {
        "asset_id": asset_id,
        "book_id": "b1",
        "knowledge_id": "k1",
        "type": "CONCEPT",
        "content": content,
        "created_at": "2026-01-01T00:00:00+00:00",
    }


def test_main_reads_topics_and_assets_and_prints_page_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    topics_path = tmp_path / "topic.json"
    assets_path = tmp_path / "asset.json"
    topics_path.write_text(
        json.dumps([_topic("topic-001", "黑天鹅", ["c1"])]),
        encoding="utf-8",
    )
    assets_path.write_text(
        json.dumps([_asset("c1", "极不可能却影响巨大的事件")]),
        encoding="utf-8",
    )

    notion = _RecordingNotion()
    monkeypatch.setattr(writer_cli, "FakeLLMClient", _CannedLLM)
    monkeypatch.setattr(
        "arkmind.notion.notion_client.NotionClient.from_env",
        classmethod(lambda cls: notion),
    )
    monkeypatch.setattr(
        "sys.argv",
        ["arkmind-writer", str(topics_path), str(assets_path)],
    )
    writer_cli.main()

    out = capsys.readouterr().out
    assert "Created Notion Page" in out
    assert "Page ID: page_001" in out
    # The canned response (with H1) lands in Notion verbatim; no file is written.
    assert notion.stored == [("黑天鹅", "# 黑天鹅\n\n极不可能却影响巨大的事件")]


def test_main_handles_empty_input(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    topics_path = tmp_path / "topic.json"
    assets_path = tmp_path / "asset.json"
    topics_path.write_text(json.dumps([]), encoding="utf-8")
    assets_path.write_text(json.dumps([]), encoding="utf-8")

    notion = _RecordingNotion()
    monkeypatch.setattr(writer_cli, "FakeLLMClient", _CannedLLM)
    monkeypatch.setattr(
        "arkmind.notion.notion_client.NotionClient.from_env",
        classmethod(lambda cls: notion),
    )
    monkeypatch.setattr(
        "sys.argv",
        ["arkmind-writer", str(topics_path), str(assets_path)],
    )
    writer_cli.main()

    assert "Page ID: page_001" in capsys.readouterr().out


def test_build_llm_defaults_to_fake() -> None:
    assert isinstance(_build_llm("fake", None), FakeLLMClient)


def test_build_llm_real_requires_model() -> None:
    with pytest.raises(SystemExit):
        _build_llm("real", None)


def test_build_llm_real_builds_openai_compatible(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARKMIND_LLM_API_KEY", "sk-test")
    monkeypatch.delenv("ARKMIND_LLM_BASE_URL", raising=False)
    assert isinstance(_build_llm("real", "deepseek-v4-pro"), OpenAICompatibleClient)
