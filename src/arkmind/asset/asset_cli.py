"""CLI entry point for Asset extraction.

Usage::

    arkmind-asset <input.json> <output.json>

Reads a Knowledge JSON array (as produced by the Dataset Runner), runs the
AssetExtractor and writes the resulting Assets as a JSON array. No business
logic lives here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from arkmind.asset.extractor import AssetExtractor
from arkmind.knowledge.models import Knowledge


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-asset")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    knowledge = [Knowledge.model_validate(item) for item in raw]

    assets = AssetExtractor().extract(knowledge)

    Path(args.output).write_text(
        json.dumps(
            [asset.model_dump(mode="json") for asset in assets],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
