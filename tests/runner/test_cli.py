"""Tests for the arkmind-run CLI (RFC-0008)."""

from __future__ import annotations

from pathlib import Path

import pytest

from arkmind.runner import cli


def test_main_resolves_source_id_to_source_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[Path] = []
    monkeypatch.setattr(
        "arkmind.runner.cli.DatasetRunner.run",
        lambda self, source_dir: captured.append(source_dir),
    )
    monkeypatch.setattr("sys.argv", ["arkmind-run", "sqlite-create-table-3.46"])
    cli.main()
    assert captured == [Path("sources") / "sqlite-create-table-3.46"]
