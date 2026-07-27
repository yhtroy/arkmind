"""SourceProvider abstraction (RFC-0002)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class SourceProvider(ABC):
    """Read a frozen Source into per-page text."""

    @abstractmethod
    def extract(self, source: Path) -> list[str]:
        """Return per-page UTF-8 text, ordered to match the PDF page order.

        The list index equals the page number minus one; an empty page
        returns ``""``.
        """
