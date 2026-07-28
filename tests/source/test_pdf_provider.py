"""Tests for PdfSourceProvider (RFC-0002)."""

from __future__ import annotations

from pathlib import Path

import pymupdf
import pytest

from arkmind.source.exceptions import SourceNotFoundError, SourceReadError
from arkmind.source.pdf_provider import PdfSourceProvider


def _make_pdf(path: Path, pages: list[str]) -> None:
    document = pymupdf.open()
    for text in pages:
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)
    document.save(str(path))
    document.close()


def test_extract_normal_pdf(tmp_path: Path) -> None:
    pdf = tmp_path / "doc.pdf"
    _make_pdf(pdf, ["Hello", "", "World"])
    result = PdfSourceProvider().extract(pdf)
    assert len(result) == 3
    assert "Hello" in result[0]
    assert result[1].strip() == ""
    assert "World" in result[2]


def test_extract_empty_pdf(tmp_path: Path) -> None:
    pdf = tmp_path / "empty.pdf"
    _make_pdf(pdf, [""])
    result = PdfSourceProvider().extract(pdf)
    assert len(result) == 1
    assert result[0].strip() == ""


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(SourceNotFoundError):
        PdfSourceProvider().extract(tmp_path / "nope.pdf")


def test_corrupt_pdf_raises_source_read_error(tmp_path: Path) -> None:
    pdf = tmp_path / "broken.pdf"
    pdf.write_bytes(b"this is not a valid pdf at all")
    with pytest.raises(SourceReadError):
        PdfSourceProvider().extract(pdf)


def test_falls_back_to_pdfplumber_when_pymupdf_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = tmp_path / "doc.pdf"
    _make_pdf(pdf, ["Fallback text"])

    def _boom(*args: object, **kwargs: object) -> object:
        raise RuntimeError("pymupdf unavailable")

    monkeypatch.setattr("arkmind.source.pdf_provider.pymupdf.open", _boom)
    result = PdfSourceProvider().extract(pdf)
    assert "Fallback text" in result[0]
