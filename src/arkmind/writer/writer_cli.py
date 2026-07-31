"""CLI entry point for the Writer (M3 Writer, Task-001 skeleton).

Usage::

    arkmind-writer <topic.json> <article.md>

Reads a Topic JSON array (as produced by ``arkmind-topic``) and writes a single
Markdown article. No business logic lives here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from arkmind.topic import Topic
from arkmind.writer.writer_service import WriterService


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-writer")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    topics = [Topic.model_validate(item) for item in raw]

    article = WriterService().write(topics)

    Path(args.output).write_text(
        f"# {article.title}\n\n{article.body}\n",
        encoding="utf-8",
    )
