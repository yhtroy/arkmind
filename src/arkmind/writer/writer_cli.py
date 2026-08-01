"""CLI entry point for the Writer (M3 Writer, M5 Task-003).

Usage::

    arkmind-writer <topic.json> <asset.json> [--provider {fake,real}] [--model NAME]

Reads a Topic JSON array (``arkmind-topic``) plus an Asset JSON array
(``arkmind-asset``), builds an in-memory Asset repository so the Writer can
resolve each Topic's asset_id references to full content, then drives the Writer
to generate content and store it in Notion (the System of Record). The CLI
prints the created Notion page id; no Markdown file is written.

The provider defaults to ``fake`` (offline, deterministic) so tests and CI never
touch the network or consume API credits. ``--provider real`` selects the
OpenAI-compatible client, configured via ``ARKMIND_LLM_API_KEY`` /
``ARKMIND_LLM_BASE_URL`` and the ``--model`` argument — the same Runtime style as
``arkmind-asset``. The Notion client is configured via ``ARKMIND_NOTION_TOKEN`` /
``ARKMIND_NOTION_DATABASE_ID``. No business logic lives here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from arkmind.asset import Asset, AssetRepository
from arkmind.runtime import (
    FakeLLMClient,
    LLMClient,
    ModelConfig,
    OpenAICompatibleClient,
)
from arkmind.topic import Topic
from arkmind.writer.writer_service import WriterService


def _build_llm(provider: str, model: str | None) -> LLMClient:
    if provider == "real":
        if not model:
            raise SystemExit("--model is required when --provider real")
        return OpenAICompatibleClient.from_env(ModelConfig(model=model))
    return FakeLLMClient()


def _load_assets(path: Path) -> AssetRepository:
    repository = AssetRepository()
    for item in json.loads(path.read_text(encoding="utf-8")):
        repository.add(Asset.model_validate(item))
    return repository


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-writer")
    parser.add_argument("topics")
    parser.add_argument("assets")
    parser.add_argument("--provider", choices=["fake", "real"], default="fake")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    raw = json.loads(Path(args.topics).read_text(encoding="utf-8"))
    topics = [Topic.model_validate(item) for item in raw]
    assets = _load_assets(Path(args.assets))

    llm = _build_llm(args.provider, args.model)
    page_id = WriterService(llm=llm).write(topics, assets)

    print("Created Notion Page")
    print(f"Page ID: {page_id}")
