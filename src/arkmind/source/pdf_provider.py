"""PdfSourceProvider — extract per-page text from a PDF (RFC-0002).

PyMuPDF is the primary reader; pdfplumber is used only when PyMuPDF raises.
An empty page yields ``""`` and never triggers the fallback.
"""

from __future__ import annotations

from pathlib import Path

import pdfplumber
import pymupdf

from arkmind.source.exceptions import SourceNotFoundError, SourceReadError
from arkmind.source.provider import SourceProvider


class PdfSourceProvider(SourceProvider):
    """Read a PDF at ``sources/<id>/original`` into per-page text."""

    def extract(self, source: Path) -> list[str]:
        if not source.is_file():
            raise SourceNotFoundError(str(source))
        try:
            return self._extract_with_pymupdf(source)
        except Exception:  # noqa: BLE001 -- RFC-0002: fall back on any PyMuPDF failure
            try:
                return self._extract_with_pdfplumber(source)
            except Exception as error:
                raise SourceReadError(str(source)) from error

    @staticmethod
    def _extract_with_pymupdf(source: Path) -> list[str]:
        with pymupdf.open(source) as document:
            return [page.get_text() for page in document]

    @staticmethod
    def _extract_with_pdfplumber(source: Path) -> list[str]:
        with pdfplumber.open(source) as pdf:
            return [(page.extract_text() or "") for page in pdf.pages]
