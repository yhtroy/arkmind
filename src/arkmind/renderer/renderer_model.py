"""Renderer data model (M4 Renderer).

The Renderer turns a Writer article into a publish-ready document. It is *not* a
second Writer: it never rewrites, summarises, adds or removes content — it only
converts format. ``RenderedArticle`` is the in-memory result before the CLI
serialises it to ``published.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RenderedArticle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str
