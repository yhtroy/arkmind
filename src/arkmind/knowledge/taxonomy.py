"""KnowledgeTaxonomy — rule-based classification of Knowledge (RFC-0005).

Assigns ``Knowledge.kind`` using ordered keyword rules: the first matching
rule wins and no Knowledge receives more than one kind. Keyword matching is
case-insensitive. Knowledge that matches no rule becomes ``"unknown"``.
No AI/LLM, no learning, no inference.
"""

from __future__ import annotations

from arkmind.knowledge.models import Knowledge

_CONSTRAINT = ("must", "shall", "required")
_WARNING = ("warning", "caution", "danger")
_EXAMPLE = ("example", "e.g.")
_DEFINITION = ("define", "definition", "is defined as")
_REFERENCE = ("see", "refer to")


class KnowledgeTaxonomy:
    """Classify each Knowledge into a canonical kind by ordered rules."""

    def classify(self, knowledge: list[Knowledge]) -> list[Knowledge]:
        for item in knowledge:
            item.kind = self._kind(item.text)
        return knowledge

    @staticmethod
    def _kind(text: str) -> str:
        lowered = text.lower()
        if any(keyword in lowered for keyword in _CONSTRAINT):
            return "constraint"
        if any(keyword in lowered for keyword in _WARNING):
            return "warning"
        if any(keyword in lowered for keyword in _EXAMPLE):
            return "example"
        if any(keyword in lowered for keyword in _DEFINITION):
            return "definition"
        if any(keyword in lowered for keyword in _REFERENCE):
            return "reference"
        if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
            return "quote"
        return "unknown"
