"""Tests for the arkmind-writer CLI skeleton (M3 Writer, Task-001).

Exercise the chain: read topic.json -> WriterService -> article.md, plus the
empty-input edge case.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arkmind.writer import writer_cli


def _topic(topic_id: str, title: str) -> dict[str, object]:
    return {
        "topic_id": topic_id,
        "title": title,
        "concepts": [],
        "definitions": [],
        "quotes": [],
    }


def test_main_reads_topics_and_writes_markdown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path = tmp_path / "topic.json"
    output_path = tmp_path / "article.md"
    input_path.write_text(
        json.dumps([_topic("topic-001", "黑天鹅"), _topic("topic-002", "极端斯坦")]),
        encoding="utf-8",
    )

    monkeypatch.setattr("sys.argv", ["arkmind-writer", str(input_path), str(output_path)])
    writer_cli.main()

    article = output_path.read_text(encoding="utf-8")
    assert article.startswith("# ")
    assert "黑天鹅" in article
    assert "极端斯坦" in article


def test_main_handles_empty_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_path = tmp_path / "topic.json"
    output_path = tmp_path / "article.md"
    input_path.write_text(json.dumps([]), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["arkmind-writer", str(input_path), str(output_path)])
    writer_cli.main()

    assert output_path.read_text(encoding="utf-8").startswith("# ")
