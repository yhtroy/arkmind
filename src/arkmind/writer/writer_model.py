"""Writer data model (M3 Writer, Task-001 skeleton).

The Writer turns a set of Topics into a single article. ``Article`` is the
in-memory representation before serialisation to Markdown; the CLI renders it to
``article.md``. Content generation (title, prose, structure) is the job of the
LLM in later M3 tasks — this skeleton only defines the shape and a placeholder
path so the pipeline can close end to end.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Article(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    body: str
