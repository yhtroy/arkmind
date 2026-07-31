"""Tests for the arkmind-writer CLI (M3 Writer, Task-003).

Exercise the chain: read topic.json + asset.json -> WriterService (offline
FakeLLM) -> article.md, plus the empty-input edge case. No network or API key.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arkmind.writer import writer_cli


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


def test_main_reads_topics_and_assets_and_writes_markdown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    topics_path = tmp_path / "topic.json"
    assets_path = tmp_path / "asset.json"
    output_path = tmp_path / "article.md"
    topics_path.write_text(
        json.dumps([_topic("topic-001", "黑天鹅", ["c1"])]),
        encoding="utf-8",
    )
    assets_path.write_text(
        json.dumps([_asset("c1", "极不可能却影响巨大的事件")]),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["arkmind-writer", str(topics_path), str(assets_path), str(output_path)],
    )
    writer_cli.main()

    article = output_path.read_text(encoding="utf-8")
    # FakeLLM echoes the Context, so the resolved asset content lands in article.md.
    assert "黑天鹅" in article
    assert "极不可能却影响巨大的事件" in article


def test_main_handles_empty_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    topics_path = tmp_path / "topic.json"
    assets_path = tmp_path / "asset.json"
    output_path = tmp_path / "article.md"
    topics_path.write_text(json.dumps([]), encoding="utf-8")
    assets_path.write_text(json.dumps([]), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["arkmind-writer", str(topics_path), str(assets_path), str(output_path)],
    )
    writer_cli.main()

    assert output_path.exists()
