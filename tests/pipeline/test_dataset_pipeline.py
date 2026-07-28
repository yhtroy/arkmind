"""Tests for DatasetPipeline (RFC-0007)."""

from __future__ import annotations

from pathlib import Path

import pytest

from arkmind.pipeline.dataset_pipeline import DatasetPipeline
from arkmind.pipeline.models import DatasetResult

_SOURCE_ID = "dataset-0001"
_DUMMY_PDF = Path("dummy.pdf")


def _patch_pages(monkeypatch: pytest.MonkeyPatch, pages: list[str]) -> None:
    # The pipeline builds PdfSourceProvider internally, so stub its extract to
    # feed deterministic page text without depending on a real PDF layout.
    monkeypatch.setattr(
        "arkmind.pipeline.dataset_pipeline.PdfSourceProvider.extract",
        lambda self, source: pages,
    )


def test_full_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_pages(monkeypatch, ["Intro must comply\n\nSee appendix B"])
    result = DatasetPipeline().run(_SOURCE_ID, _DUMMY_PDF)
    assert isinstance(result, DatasetResult)
    assert result.source_id == _SOURCE_ID
    assert [f.text for f in result.fragments] == ["Intro must comply", "See appendix B"]
    assert [k.text for k in result.knowledge] == ["Intro must comply", "See appendix B"]
    assert len(result.provenance) == 2


def test_empty_pdf(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_pages(monkeypatch, [""])
    result = DatasetPipeline().run(_SOURCE_ID, _DUMMY_PDF)
    assert isinstance(result, DatasetResult)
    assert result.fragments == []
    assert result.knowledge == []
    assert result.provenance == []


def test_taxonomy_applied(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_pages(monkeypatch, ["You must stop\n\nSee the manual\n\nplain body"])
    result = DatasetPipeline().run(_SOURCE_ID, _DUMMY_PDF)
    assert [k.kind for k in result.knowledge] == ["constraint", "reference", "unknown"]


def test_provenance_count_matches_knowledge(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_pages(monkeypatch, ["a\n\nb\n\nc"])
    result = DatasetPipeline().run(_SOURCE_ID, _DUMMY_PDF)
    assert len(result.provenance) == len(result.knowledge) == 3


def test_source_id_propagated(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_pages(monkeypatch, ["one\n\ntwo"])
    result = DatasetPipeline().run(_SOURCE_ID, _DUMMY_PDF)
    assert result.source_id == _SOURCE_ID
    assert all(k.source_id == _SOURCE_ID for k in result.knowledge)
    assert all(p.source_id == _SOURCE_ID for p in result.provenance)


def test_output_order_preserved(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_pages(monkeypatch, ["p1a\n\np1b", "p2a\n\np2b"])
    result = DatasetPipeline().run(_SOURCE_ID, _DUMMY_PDF)
    texts = ["p1a", "p1b", "p2a", "p2b"]
    assert [f.text for f in result.fragments] == texts
    assert [k.text for k in result.knowledge] == texts
    assert [p.knowledge_id for p in result.provenance] == [k.knowledge_id for k in result.knowledge]
