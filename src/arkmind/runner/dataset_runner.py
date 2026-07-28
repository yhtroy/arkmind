"""DatasetRunner — run the Dataset pipeline for one Source and write JSON (RFC-0008).

Given a Source directory (``sources/<id>/`` holding ``source.yaml`` and
``original``), it loads metadata via the Source Registry, runs the Dataset
Pipeline once, and writes ``knowledge.json``, ``provenance.json`` and
``summary.json`` under ``<source_dir>/output``. Pure orchestration: no business
logic, no PDF re-parsing; module exceptions propagate unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path

from arkmind.pipeline.dataset_pipeline import DatasetPipeline
from arkmind.source.registry import SourceRegistry

_ORIGINAL_NAME = "original"
_OUTPUT_DIR = "output"


class DatasetRunner:
    """Run one Source through the pipeline and persist JSON artifacts."""

    def run(self, source_dir: Path) -> None:
        source_dir = Path(source_dir)
        metadata = SourceRegistry(source_dir.parent)._load(source_dir.name)

        result = DatasetPipeline().run(
            source_id=metadata.id,
            pdf_path=source_dir / _ORIGINAL_NAME,
        )

        output_dir = source_dir / _OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        self._write_json(
            output_dir / "knowledge.json",
            [item.model_dump(mode="json") for item in result.knowledge],
        )
        self._write_json(
            output_dir / "provenance.json",
            [item.model_dump(mode="json") for item in result.provenance],
        )
        self._write_json(
            output_dir / "summary.json",
            {
                "source_id": result.source_id,
                "fragments": len(result.fragments),
                "knowledge": len(result.knowledge),
                "provenance": len(result.provenance),
            },
        )

    @staticmethod
    def _write_json(path: Path, data: object) -> None:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
