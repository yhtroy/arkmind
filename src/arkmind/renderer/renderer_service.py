"""Renderer service (M4 Renderer, Task-001 Skeleton).

Converts a Writer article into a publish-ready document:

    article (Markdown) -> RendererService.render -> RenderedArticle (Markdown)

The Renderer only converts *format*. It performs basic Markdown whitespace
normalisation — collapsing runs of blank lines into one and trimming trailing
spaces plus leading/trailing blank lines — which is loss-less: no heading, word,
paragraph or ordering is ever changed, added or removed. It never rewrites the
title, summarises, reorganises content or calls an LLM. The document title is
preserved verbatim (normalisation never drops the first heading).

Since Task-002 the service also validates that the article carries a legal
level-1 heading via :class:`HeadlineValidator`; a missing H1 raises
:class:`MissingH1Error` and no ``RenderedArticle`` is produced.
"""

from __future__ import annotations

from arkmind.renderer.headline_validator import HeadlineValidator
from arkmind.renderer.renderer_model import RenderedArticle


class RendererService:
    """Convert a Writer article into a publish-ready document (format only)."""

    def __init__(self, headline_validator: HeadlineValidator | None = None) -> None:
        self._headline_validator = (
            headline_validator if headline_validator is not None else HeadlineValidator()
        )

    def render(self, article: str) -> RenderedArticle:
        content = self._normalize(article)
        self._headline_validator.validate(content)
        return RenderedArticle(content=content)

    def _normalize(self, text: str) -> str:
        lines = [line.rstrip() for line in text.splitlines()]

        collapsed: list[str] = []
        for line in lines:
            if line == "" and collapsed and collapsed[-1] == "":
                continue  # collapse consecutive blank lines into a single one
            collapsed.append(line)

        while collapsed and collapsed[0] == "":
            collapsed.pop(0)
        while collapsed and collapsed[-1] == "":
            collapsed.pop()

        return "\n".join(collapsed)
