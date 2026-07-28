"""Pipeline layer: orchestrate all modules into a DatasetResult (RFC-0007)."""

from arkmind.pipeline.dataset_pipeline import DatasetPipeline
from arkmind.pipeline.models import DatasetResult

__all__ = ["DatasetPipeline", "DatasetResult"]
