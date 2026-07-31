"""CLI entry point for the Publisher (M5 Publisher, Task-001).

Usage::

    arkmind-publisher <article.json>

Reads an ``Article`` from a JSON file, then publishes it to the destination
database. It never writes Markdown or any other file — the output is a page in
Notion. The client is built from the ``ARKMIND_NOTION_*`` environment (the same
Runtime style as ``arkmind-writer``); no business logic lives here.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from arkmind.publisher.article import Article
from arkmind.publisher.notion_client import NotionClient
from arkmind.publisher.publisher import Publisher, PublisherClient


def _build_client() -> PublisherClient:
    return NotionClient.from_env()


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-publisher")
    parser.add_argument("article")
    args = parser.parse_args()

    article = Article.model_validate_json(Path(args.article).read_text(encoding="utf-8"))
    Publisher(_build_client()).publish(article)
    print("Published")
