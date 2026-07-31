"""Article data model (M5 Publisher, Task-001).

``Article`` is the frozen product-level output object of the pipeline
(``Writer -> Article -> Publisher -> Notion``). Per the V2.0 architecture it is
an in-memory object, never a file: the CLI deserialises it from JSON and hands
it straight to the Publisher.

The shape is frozen by the M5 architecture — fields may be added later, never
removed::

    Article : id, title, content, metadata
    metadata: book, author, created_at, word_count, topic_count, asset_count
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArticleMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book: str
    author: str
    created_at: datetime
    word_count: int
    topic_count: int
    asset_count: int


class Article(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    content: str
    metadata: ArticleMetadata
