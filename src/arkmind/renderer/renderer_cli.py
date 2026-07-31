"""CLI entry point for the Renderer (M4 Renderer, Task-001 Skeleton).

Usage::

    arkmind-renderer <article.md> <wechat.md>

Reads a Writer article (UTF-8 Markdown), runs it through the Renderer (format-only
normalisation + H1 validation) and writes the WeChat (公众号) Markdown document.
If the article lacks a legal level-1 heading the run fails with ``Missing H1
title.`` and a non-zero exit, and no output is written. No business logic, no
LLM, no platform strategy lives here.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from arkmind.renderer.headline_validator import MissingH1Error
from arkmind.renderer.renderer_service import RendererService


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-renderer")
    parser.add_argument("article")
    parser.add_argument("output")
    args = parser.parse_args()

    article = Path(args.article).read_text(encoding="utf-8")
    try:
        rendered = RendererService().render(article)
    except MissingH1Error as exc:
        raise SystemExit(str(exc)) from exc

    text = f"{rendered.content}\n" if rendered.content else ""
    Path(args.output).write_text(text, encoding="utf-8")
