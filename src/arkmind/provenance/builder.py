"""ProvenanceBuilder — trace each Knowledge to its Source and Fragment (RFC-0006).

One Provenance per Knowledge; ``knowledge_id``, ``fragment_id`` and
``source_id`` are copied verbatim (no derivation, no value change, no new
ids). Output order matches the input order.
"""

from __future__ import annotations

from arkmind.knowledge.models import Knowledge
from arkmind.provenance.models import Provenance


class ProvenanceBuilder:
    """Build one Provenance per Knowledge, preserving order."""

    def build(self, knowledge: list[Knowledge]) -> list[Provenance]:
        return [
            Provenance(
                knowledge_id=item.knowledge_id,
                fragment_id=item.fragment_id,
                source_id=item.source_id,
            )
            for item in knowledge
        ]
