"""CLI entry point for the Writer (M3 Writer).

Usage::

    arkmind-writer <topic.json> <asset.json> <article.md>

Reads a Topic JSON array (``arkmind-topic``) plus an Asset JSON array
(``arkmind-asset``), builds an in-memory Asset repository so the Writer can
resolve each Topic's asset_id references to full content, then drives the Writer
to produce a single Markdown article.

The Writer uses the offline :class:`FakeLLMClient` by default, so this command
runs without an API key or network. Real-provider selection lands in Task-004.
No business logic lives here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from arkmind.asset import Asset, AssetRepository
from arkmind.topic import Topic
from arkmind.writer.writer_service import WriterService


def _load_assets(path: Path) -> AssetRepository:
    repository = AssetRepository()
    for item in json.loads(path.read_text(encoding="utf-8")):
        repository.add(Asset.model_validate(item))
    return repository


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-writer")
    parser.add_argument("topics")
    parser.add_argument("assets")
    parser.add_argument("output")
    args = parser.parse_args()

    raw = json.loads(Path(args.topics).read_text(encoding="utf-8"))
    topics = [Topic.model_validate(item) for item in raw]
    assets = _load_assets(Path(args.assets))

    article = WriterService().write(topics, assets)

    Path(args.output).write_text(f"{article.markdown}\n", encoding="utf-8")
