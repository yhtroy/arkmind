"""Tests for the arkmind-asset CLI (TASK-002.5)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arkmind.asset import asset_cli


def _knowledge_item(knowledge_id: str = "k1") -> dict[str, object]:
    return {
        "knowledge_id": knowledge_id,
        "fragment_id": "f1",
        "source_id": "book-1",
        "text": "long-term thinking",
    }


def test_main_reads_knowledge_and_writes_assets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "asset.json"
    input_path.write_text(json.dumps([_knowledge_item()]), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["arkmind-asset", str(input_path), str(output_path)])
    asset_cli.main()

    assert json.loads(output_path.read_text(encoding="utf-8")) == []


def test_main_handles_empty_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "asset.json"
    input_path.write_text(json.dumps([]), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["arkmind-asset", str(input_path), str(output_path)])
    asset_cli.main()

    assert json.loads(output_path.read_text(encoding="utf-8")) == []
