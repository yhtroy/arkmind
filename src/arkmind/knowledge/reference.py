"""KnowledgeReferenceDetector — deterministic REFERENCES edges (RFC-0013).

The first Knowledge-to-Knowledge relation in the graph: scan each
``Knowledge.text`` with the regex ``\\bST_[A-Za-z]+\\b`` and emit one
``KnowledgeReference`` per match. Matches are kept in Knowledge order, then in
text order; duplicates are preserved and nothing is sorted. No AI, no fuzzy
matching, no inference. Does not modify Knowledge and is not wired into the
pipeline (deferred to RFC-0014).
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict

from arkmind.knowledge.models import Knowledge

_FUNCTION = re.compile(r"\bST_[A-Za-z]+\b")


class KnowledgeReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    from_knowledge_id: str
    to_function: str


class KnowledgeReferenceDetector:
    """Extract explicit ``ST_*`` function references from Knowledge text."""

    def detect(self, knowledge: list[Knowledge]) -> list[KnowledgeReference]:
        references: list[KnowledgeReference] = []
        for item in knowledge:
            for match in _FUNCTION.finditer(item.text):
                references.append(
                    KnowledgeReference(
                        source_id=item.source_id,
                        from_knowledge_id=item.knowledge_id,
                        to_function=match.group(),
                    )
                )
        return references
