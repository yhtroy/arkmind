"""Tests for the arkmind-topic CLI (RFC-M2.2-001).

Exercise the full chain: read asset.json -> TopicBuilder -> topic.json, and the
empty-input edge case.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arkmind.topic import topic_cli


def _asset(asset_type: str, content: str, asset_id: str) -> dict[str, object]:
    return {
        "asset_id": asset_id,
        "book_id": "b1",
        "knowledge_id": "k1",
        "type": asset_type,
        "content": content,
        "created_at": "2026-01-01T00:00:00Z",
    }


def test_main_reads_assets_and_writes_topics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path = tmp_path / "asset.json"
    output_path = tmp_path / "topic.json"
    input_path.write_text(
        json.dumps(
            [
                _asset("CONCEPT", "Concept:\n黑天鹅\nDescription:\nd\nSignificance:\ns", "a1"),
                _asset("DEFINITION", "Term:\n黑天鹅\nDefinition:\nd\nBoundary:\nb", "a2"),
                _asset("QUOTE", "关于黑天鹅的一句话", "q1"),
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("sys.argv", ["arkmind-topic", str(input_path), str(output_path)])
    topic_cli.main()

    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(result) == 1
    assert result[0]["title"] == "黑天鹅"
    assert result[0]["concepts"] == ["a1"]
    assert result[0]["definitions"] == ["a2"]
    assert result[0]["quotes"] == ["q1"]


def test_main_handles_empty_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_path = tmp_path / "asset.json"
    output_path = tmp_path / "topic.json"
    input_path.write_text(json.dumps([]), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["arkmind-topic", str(input_path), str(output_path)])
    topic_cli.main()

    assert json.loads(output_path.read_text(encoding="utf-8")) == []
