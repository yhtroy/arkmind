"""Tests for the arkmind-renderer CLI (M4 Renderer, Task-001 Skeleton).

Exercise the chain: read article.md -> RendererService -> published.md, with
UTF-8 round-tripping and empty-input handling. No network, no LLM.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from arkmind.renderer import renderer_cli


def test_main_reads_article_and_writes_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    article_path = tmp_path / "article.md"
    output_path = tmp_path / "wechat.md"
    article_path.write_text("# 黑天鹅\n\n极不可能却影响巨大的事件。", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["arkmind-renderer", str(article_path), str(output_path)],
    )
    renderer_cli.main()

    published = output_path.read_text(encoding="utf-8")
    # UTF-8 content round-trips loss-less; nothing is rewritten.
    assert "# 黑天鹅" in published
    assert "极不可能却影响巨大的事件。" in published


def test_main_fails_when_no_h1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    article_path = tmp_path / "article.md"
    output_path = tmp_path / "wechat.md"
    article_path.write_text("正文没有一级标题。", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["arkmind-renderer", str(article_path), str(output_path)],
    )
    with pytest.raises(SystemExit) as excinfo:
        renderer_cli.main()

    assert excinfo.value.code == "Missing H1 title."
    # Validation fails before writing: no output document is produced.
    assert not output_path.exists()


def test_main_fails_on_empty_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    article_path = tmp_path / "article.md"
    output_path = tmp_path / "wechat.md"
    article_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["arkmind-renderer", str(article_path), str(output_path)],
    )
    with pytest.raises(SystemExit):
        renderer_cli.main()

    assert not output_path.exists()
