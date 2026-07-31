"""Publisher — the sole output layer (M5 Publisher, Task-001).

The Publisher is a pure Adapter. Its only job is::

    publish(article)

It never modifies the title, never modifies the content, and never uses AI,
prompts, SEO, tags, or rewriting. It moves an ``Article`` from memory to a
destination database and nothing else.

To stay decoupled from any specific destination SDK, the Publisher depends on
the ``PublisherClient`` abstraction rather than on Notion directly. ``NotionClient``
is the concrete client today; swapping in Obsidian / MongoDB / Postgres / a Wiki
later means providing a different ``PublisherClient`` — the Publisher does not
change.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from arkmind.publisher.article import Article


class PublisherClient(ABC):
    """Destination client contract: turn an ``Article`` into a stored record."""

    @abstractmethod
    def publish(self, article: Article) -> None:
        """Persist ``article`` to the destination."""


class Publisher:
    """Move an ``Article`` from memory to a destination via a ``PublisherClient``."""

    def __init__(self, client: PublisherClient) -> None:
        self._client = client

    def publish(self, article: Article) -> None:
        self._client.publish(article)
