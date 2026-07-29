"""KnowledgeDeduplicator — deterministic duplicate marking (RFC-0012).

Scans Knowledge in input order and flags duplicates using ``normalized`` as the
unique key: the first occurrence of a key stays ``duplicate=False``, every later
occurrence is marked ``duplicate=True``. No item is removed or reordered, and no
field other than ``duplicate`` is modified.
"""

from __future__ import annotations

from arkmind.knowledge.models import Knowledge


class KnowledgeDeduplicator:
    """Mark repeated Knowledge (by ``normalized``) without dropping or reordering."""

    def deduplicate(self, knowledge: list[Knowledge]) -> list[Knowledge]:
        seen: set[str | None] = set()
        result: list[Knowledge] = []
        for item in knowledge:
            is_duplicate = item.normalized in seen
            seen.add(item.normalized)
            result.append(item.model_copy(update={"duplicate": is_duplicate}))
        return result
