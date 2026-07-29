"""Knowledge layer: one Knowledge per Fragment (RFC-0004)."""

from arkmind.knowledge.deduplicator import KnowledgeDeduplicator
from arkmind.knowledge.extractor import KnowledgeExtractor
from arkmind.knowledge.models import Knowledge
from arkmind.knowledge.normalizer import KnowledgeNormalizer
from arkmind.knowledge.reference import KnowledgeReference, KnowledgeReferenceDetector

__all__ = [
    "Knowledge",
    "KnowledgeDeduplicator",
    "KnowledgeExtractor",
    "KnowledgeNormalizer",
    "KnowledgeReference",
    "KnowledgeReferenceDetector",
]
