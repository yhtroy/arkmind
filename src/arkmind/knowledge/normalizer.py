"""KnowledgeNormalizer — deterministic, AI-free text normalization (RFC-0011).

Fills each Knowledge's ``normalized`` field from its ``text`` by applying, in a
fixed order: trim, collapse consecutive whitespace to a single space, drop a
single trailing ``.``, and strip Markdown markers. Case is preserved, no word is
deleted/replaced/added, and the original ``text`` is never modified.

Markdown stripping is intentionally conservative to protect the technical corpus
(identifiers such as ``ST_Area``, SQL ``SELECT *`` and function signatures with
parentheses): only paired emphasis (``**bold**``, ``*italic*``), paired inline
code (``` `code` ```) and leading block markers (``#`` heading, ``>`` quote) are
removed. Lone ``*`` / backticks, underscores and parentheses are left untouched.
No LLM, summary, translation or semantic change is performed.
"""

from __future__ import annotations

import re

from arkmind.knowledge.models import Knowledge

_WHITESPACE = re.compile(r"\s+")
_LEADING_HEADING = re.compile(r"^#+\s*")
_LEADING_QUOTE = re.compile(r"^>\s*")
_BOLD = re.compile(r"\*\*([^*]+?)\*\*")
_ITALIC = re.compile(r"\*([^*]+?)\*")
_INLINE_CODE = re.compile(r"`([^`]+?)`")


class KnowledgeNormalizer:
    """Populate ``normalized`` for every Knowledge item, preserving the input."""

    def normalize(self, knowledge: list[Knowledge]) -> list[Knowledge]:
        return [
            item.model_copy(update={"normalized": self._normalize_text(item.text)})
            for item in knowledge
        ]

    @staticmethod
    def _normalize_text(text: str) -> str:
        result = text.strip()
        result = _WHITESPACE.sub(" ", result)
        result = result.removesuffix(".")
        result = _LEADING_HEADING.sub("", result)
        result = _LEADING_QUOTE.sub("", result)
        result = _BOLD.sub(r"\1", result)
        result = _ITALIC.sub(r"\1", result)
        result = _INLINE_CODE.sub(r"\1", result)
        return result
