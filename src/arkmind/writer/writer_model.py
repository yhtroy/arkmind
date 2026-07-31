"""Writer data model (M3 Writer).

The Writer turns a set of Topics into a single article. ``Article`` is the
in-memory representation before serialisation to Markdown; the CLI renders it to
``article.md``. Since Task-003 the ``markdown`` field holds the LLM response
verbatim — a complete Markdown document (title included) — so the Writer never
parses or reshapes the model output.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Article(BaseModel):
    model_config = ConfigDict(extra="forbid")

    markdown: str
