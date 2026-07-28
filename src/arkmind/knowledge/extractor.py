"""KnowledgeExtractor — one Knowledge per Fragment (RFC-0004).

Each Fragment maps to exactly one Knowledge: the text is copied verbatim (no
split, merge, reasoning or rewrite). Output order matches the input order.
``knowledge_id`` is the lowercase-hex SHA-256 of UTF-8 ``fragment_id`` and
``text`` joined by ``"\n"``.
"""

from __future__ import annotations

import hashlib

from arkmind.fragment.models import Fragment
from arkmind.knowledge.models import Knowledge


class KnowledgeExtractor:
    """Map each Fragment to a single Knowledge, preserving order."""

    def extract(self, fragments: list[Fragment]) -> list[Knowledge]:
        return [
            Knowledge(
                knowledge_id=self._knowledge_id(fragment.fragment_id, fragment.text),
                fragment_id=fragment.fragment_id,
                text=fragment.text,
            )
            for fragment in fragments
        ]

    @staticmethod
    def _knowledge_id(fragment_id: str, text: str) -> str:
        payload = f"{fragment_id}\n{text}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
