"""NotionClient — the persistence layer for the Writer (M5, Task-003).

ArkMind's System of Record is a Notion database: the Writer stores generated
content there directly, and the pipeline ends at Notion. There is no publishing
concept — content is created (``create_page``), not distributed.

This module is the single place that knows about Notion. It maps the Writer's
output onto a Notion database page and creates it via the Notion REST API.
Deliberately dependency-free: the HTTP call uses the standard library
(``urllib.request``) rather than a third-party Notion SDK, keeping the
dependency whitelist unchanged. When an official SDK is approved, only this
file changes.

Credentials follow the existing ``ARKMIND_*`` runtime convention (see
``arkmind.runtime.config``):

* ``ARKMIND_NOTION_TOKEN`` — Notion integration token (required).
* ``ARKMIND_NOTION_DATABASE_ID`` — target Articles database id (required).

Content -> Notion property mapping (fields frozen by the M5 architecture; the
Book / Author / Created Time / Word Count / Topic Count / Asset Count
properties are populated once the Writer output contract is frozen in a
separate RFC)::

    title   -> Title   (title)
    content -> Content (rich_text)
"""

from __future__ import annotations

import json
import os
import urllib.request

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


class NotionClient:
    """Create a page in a Notion database and return its page id."""

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

    def create_page(self, title: str, content: str) -> str:
        """Create a page from ``title`` / ``content`` and return the page id."""
        payload = json.dumps(self.build_page(title, content)).encode("utf-8")
        request = urllib.request.Request(_API_URL, data=payload, method="POST")
        request.add_header("Authorization", f"Bearer {self._token}")
        request.add_header("Notion-Version", _NOTION_VERSION)
        request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request) as response:
            page = json.loads(response.read())
        return page["id"]

    def build_page(self, title: str, content: str) -> dict[str, object]:
        """Map ``title`` / ``content`` onto a Notion ``pages.create`` request body."""
        return {
            "parent": {"database_id": self._database_id},
            "properties": {
                "Title": {"title": [{"text": {"content": title}}]},
                "Content": {"rich_text": self._rich_text(content)},
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
