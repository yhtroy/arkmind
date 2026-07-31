"""CLI entry point for the Topic Builder (RFC-M2.2-001).

Usage::

    arkmind-topic <asset.json> <topic.json>

Reads an Asset JSON array (as produced by ``arkmind-asset``) and writes the
aggregated Topics as a JSON array. No business logic lives here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from arkmind.asset import Asset
from arkmind.topic.topic_builder import TopicBuilder


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-topic")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    assets = [Asset.model_validate(item) for item in raw]

    topics = TopicBuilder().build(assets)

    Path(args.output).write_text(
        json.dumps(
            [topic.model_dump(mode="json") for topic in topics],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
