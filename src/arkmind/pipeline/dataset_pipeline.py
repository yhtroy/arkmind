"""DatasetPipeline — orchestrate all layers into a DatasetResult (RFC-0007).

Runs, in fixed order: PdfSourceProvider -> FragmentExtractor ->
KnowledgeExtractor -> KnowledgeTaxonomy -> ProvenanceBuilder. Pure
orchestration: no new business logic, and module exceptions propagate
unchanged (the pipeline catches nothing).
"""

from __future__ import annotations

from pathlib import Path

from arkmind.fragment.extractor import FragmentExtractor
from arkmind.knowledge.extractor import KnowledgeExtractor
from arkmind.knowledge.taxonomy import KnowledgeTaxonomy
from arkmind.pipeline.models import DatasetResult
from arkmind.provenance.builder import ProvenanceBuilder
from arkmind.source.pdf_provider import PdfSourceProvider


class DatasetPipeline:
    """Chain every layer from a PDF to Knowledge and Provenance."""

    def run(self, source_id: str, pdf_path: Path) -> DatasetResult:
        pages = PdfSourceProvider().extract(pdf_path)
        fragments = FragmentExtractor().extract(pages, source_id)
        knowledge = KnowledgeExtractor().extract(fragments, source_id)
        knowledge = KnowledgeTaxonomy().classify(knowledge)
        provenance = ProvenanceBuilder().build(knowledge)
        return DatasetResult(
            source_id=source_id,
            fragments=fragments,
            knowledge=knowledge,
            provenance=provenance,
        )
