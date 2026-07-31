"""CLI entry point for the Renderer (M4 Renderer, Task-001 Skeleton).

Usage::

    arkmind-renderer <article.md> <published.md>

Reads a Writer article (UTF-8 Markdown), runs it through the Renderer (format-only
normalisation) and writes the publish-ready document. No business logic, no LLM,
no platform strategy lives here.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from arkmind.renderer.renderer_service import RendererService


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-renderer")
    parser.add_argument("article")
    parser.add_argument("output")
    args = parser.parse_args()

    article = Path(args.article).read_text(encoding="utf-8")
    rendered = RendererService().render(article)

    text = f"{rendered.content}\n" if rendered.content else ""
    Path(args.output).write_text(text, encoding="utf-8")
