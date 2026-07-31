"""NotionClient — the concrete destination client for the Publisher (M5, Task-001).

This is the single place that knows about Notion. It implements the
``PublisherClient`` contract by mapping an ``Article`` onto a Notion database page
and creating it via the Notion REST API. The rest of the Publisher stays unaware
of Notion entirely; replacing this file (e.g. with the official SDK, or a
different destination) leaves ``Publisher`` untouched.

Deliberately dependency-free: the HTTP call uses the standard library
(``urllib.request``) rather than a third-party Notion SDK, keeping the M5 MVP off
the dependency whitelist. When an official SDK is approved, only this file changes.

Credentials follow the existing ``ARKMIND_*`` runtime convention (see
``arkmind.runtime.config``):

* ``ARKMIND_NOTION_TOKEN`` — Notion integration token (required).
* ``ARKMIND_NOTION_DATABASE_ID`` — target Articles database id (required).

Frozen Article -> Notion property mapping::

    title            -> Title        (title)
    content          -> Content      (rich_text)
    metadata.book    -> Book         (rich_text)
    metadata.author  -> Author       (rich_text)
    metadata.created_at   -> Created Time (date)
    metadata.word_count   -> Word Count   (number)
    metadata.topic_count  -> Topic Count  (number)
    metadata.asset_count  -> Asset Count  (number)
"""

from __future__ import annotations

import json
import os
import urllib.request

from arkmind.publisher.article import Article
from arkmind.publisher.publisher import PublisherClient

_TOKEN_ENV = "ARKMIND_NOTION_TOKEN"
_DATABASE_ENV = "ARKMIND_NOTION_DATABASE_ID"
_API_URL = "https://api.notion.com/v1/pages"
_NOTION_VERSION = "2022-06-28"
_RICH_TEXT_LIMIT = 2000


class MissingNotionConfigError(RuntimeError):
    """Raised when a required Notion environment variable is unset or empty."""

    def __init__(self, variable: str) -> None:
        super().__init__(f"{variable} is not set")
        self.variable = variable


class NotionClient(PublisherClient):
    """Create a page in a Notion database from an ``Article``."""

    def __init__(self, token: str, database_id: str) -> None:
        self._token = token
        self._database_id = database_id

    @classmethod
    def from_env(cls) -> NotionClient:
        """Build a client from ``ARKMIND_NOTION_TOKEN`` / ``ARKMIND_NOTION_DATABASE_ID``."""
        token = os.environ.get(_TOKEN_ENV)
        if not token:
            raise MissingNotionConfigError(_TOKEN_ENV)
        database_id = os.environ.get(_DATABASE_ENV)
        if not database_id:
            raise MissingNotionConfigError(_DATABASE_ENV)
        return cls(token=token, database_id=database_id)

    def publish(self, article: Article) -> None:
        payload = json.dumps(self.build_page(article)).encode("utf-8")
        request = urllib.request.Request(_API_URL, data=payload, method="POST")
        request.add_header("Authorization", f"Bearer {self._token}")
        request.add_header("Notion-Version", _NOTION_VERSION)
        request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request) as response:
            response.read()

    def build_page(self, article: Article) -> dict[str, object]:
        """Map an ``Article`` onto a Notion ``pages.create`` request body."""
        meta = article.metadata
        return {
            "parent": {"database_id": self._database_id},
            "properties": {
                "Title": {"title": [{"text": {"content": article.title}}]},
                "Content": {"rich_text": self._rich_text(article.content)},
                "Book": {"rich_text": self._rich_text(meta.book)},
                "Author": {"rich_text": self._rich_text(meta.author)},
                "Created Time": {"date": {"start": meta.created_at.isoformat()}},
                "Word Count": {"number": meta.word_count},
                "Topic Count": {"number": meta.topic_count},
                "Asset Count": {"number": meta.asset_count},
            },
        }

    @staticmethod
    def _rich_text(text: str) -> list[dict[str, object]]:
        """Split ``text`` into Notion rich-text chunks under the per-object limit."""
        if not text:
            return []
        return [
            {"text": {"content": text[start : start + _RICH_TEXT_LIMIT]}}
            for start in range(0, len(text), _RICH_TEXT_LIMIT)
        ]
