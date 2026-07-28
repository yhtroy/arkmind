"""Tests for DatasetRunner (RFC-0008)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from arkmind.runner.dataset_runner import DatasetRunner
from arkmind.source.exceptions import SourceNotFoundError

_SOURCE_ID = "sqlite-create-table-3.46"


def _make_source(tmp_path: Path, *, with_original: bool = True) -> Path:
    source_dir = tmp_path / _SOURCE_ID
    source_dir.mkdir()
    metadata = {
        "id": _SOURCE_ID,
        "title": "SQLite CREATE TABLE",
        "origin": "https://example.com/sqlite",
        "version": "3.46",
        "license": "public-domain",
    }
    (source_dir / "source.yaml").write_text(
        yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    if with_original:
        (source_dir / "original").write_bytes(b"%PDF-1.4 stub")
    return source_dir


def _patch_pages(monkeypatch: pytest.MonkeyPatch, pages: list[str]) -> None:
    monkeypatch.setattr(
        "arkmind.pipeline.dataset_pipeline.PdfSourceProvider.extract",
        lambda self, source: pages,
    )


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def test_normal_run(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_pages(monkeypatch, ["Intro must comply\n\nSee appendix B"])
    source_dir = _make_source(tmp_path)
    assert DatasetRunner().run(source_dir) is None


def test_output_dir_created(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_pages(monkeypatch, ["some body text"])
    source_dir = _make_source(tmp_path)
    assert not (source_dir / "output").exists()
    DatasetRunner().run(source_dir)
    assert (source_dir / "output").is_dir()


def test_three_json_files_exist(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_pages(monkeypatch, ["a\n\nb"])
    source_dir = _make_source(tmp_path)
    DatasetRunner().run(source_dir)
    output = source_dir / "output"
    assert (output / "knowledge.json").is_file()
    assert (output / "provenance.json").is_file()
    assert (output / "summary.json").is_file()


def test_summary_counts_correct(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_pages(monkeypatch, ["a\n\nb\n\nc"])
    source_dir = _make_source(tmp_path)
    DatasetRunner().run(source_dir)
    summary = _read_json(source_dir / "output" / "summary.json")
    assert summary == {
        "source_id": _SOURCE_ID,
        "fragments": 3,
        "knowledge": 3,
        "provenance": 3,
    }


def test_empty_dataset(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_pages(monkeypatch, [""])
    source_dir = _make_source(tmp_path)
    DatasetRunner().run(source_dir)
    output = source_dir / "output"
    assert _read_json(output / "knowledge.json") == []
    assert _read_json(output / "provenance.json") == []
    assert _read_json(output / "summary.json") == {
        "source_id": _SOURCE_ID,
        "fragments": 0,
        "knowledge": 0,
        "provenance": 0,
    }


def test_missing_original(tmp_path: Path) -> None:
    source_dir = _make_source(tmp_path, with_original=False)
    with pytest.raises(SourceNotFoundError):
        DatasetRunner().run(source_dir)
