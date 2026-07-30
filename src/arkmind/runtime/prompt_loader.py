"""Prompt loader for the AI Runtime (Runtime Contract v1).

Loads prompt bodies from ``<root>/<name>.md``: ``load("asset/concept")`` reads
``prompts/asset/concept.md``. A missing prompt raises ``PromptNotFoundError`` —
it never returns ``None``.
"""

from __future__ import annotations

from pathlib import Path

from arkmind.runtime.exceptions import PromptNotFoundError


class PromptLoader:
    """Read prompt files from a root directory by ``category/name``."""

    def __init__(self, root: Path | str = "prompts") -> None:
        self._root = Path(root)

    def load(self, name: str) -> str:
        path = self._root / f"{name}.md"
        if not path.is_file():
            raise PromptNotFoundError(name)
        return path.read_text(encoding="utf-8")
