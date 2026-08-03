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

Editorial Database schema (frozen 2026-07-27): properties carry management
metadata only — Title / Book / Author / Status / Word Count. The generated
body is written to the Page Body (``children`` blocks), never to a property.
The Page Body starts directly with the article (its level-1 heading is the
article title) and always ends with the fixed footer::

    (generated Markdown, converted to blocks)

    ---

    ## Editor Notes

    ---

    ## Review

The Markdown -> blocks conversion lives in :mod:`arkmind.notion.block_builder`
so the Writer contract (Markdown) stays untouched; Notion is the only place
that understands Notion.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

from arkmind.notion.block_builder import build_blocks

_TOKEN_ENV = "ARKMIND_NOTION_TOKEN"
_DATABASE_ENV = "ARKMIND_NOTION_DATABASE_ID"
_API_URL = "https://api.notion.com/v1/pages"
_PAGE_URL = "https://api.notion.com/v1/pages/{id}"
_BLOCKS_URL = "https://api.notion.com/v1/blocks/{id}/children"
_ME_URL = "https://api.notion.com/v1/users/me"
_DATABASES_URL = "https://api.notion.com/v1/databases/{id}"
_NOTION_VERSION = "2022-06-28"
_WHITESPACE = re.compile(r"\s+")

_EDITOR_HEADING = "Editor Notes"
_REVIEW_HEADING = "Review"


class MissingNotionConfigError(RuntimeError):
    """Raised when a required Notion environment variable is unset or empty."""

    def __init__(self, variable: str) -> None:
        super().__init__(f"{variable} is not set")
        self.variable = variable


class NotionEnvironmentError(RuntimeError):
    """Raised when an environment check fails; the message is user-actionable."""


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

    def verify_token(self) -> None:
        """Check that the token authenticates; raise :class:`NotionEnvironmentError` otherwise."""
        request = urllib.request.Request(_ME_URL, method="GET")
        request.add_header("Authorization", f"Bearer {self._token}")
        request.add_header("Notion-Version", _NOTION_VERSION)
        try:
            with urllib.request.urlopen(request):
                pass
        except urllib.error.HTTPError as error:
            if error.code in (401, 403):
                raise NotionEnvironmentError(
                    "Token is invalid or revoked — create a new secret at "
                    "https://www.notion.so/my-integrations"
                ) from error
            raise NotionEnvironmentError(f"Notion API error {error.code}") from error
        except urllib.error.URLError as error:
            raise NotionEnvironmentError(
                f"Network error while reaching Notion: {error.reason}"
            ) from error

    def verify_database(self) -> None:
        """Check that the database is reachable and shared; raise :class:`NotionEnvironmentError` otherwise."""
        request = urllib.request.Request(_DATABASES_URL.format(id=self._database_id), method="GET")
        request.add_header("Authorization", f"Bearer {self._token}")
        request.add_header("Notion-Version", _NOTION_VERSION)
        try:
            with urllib.request.urlopen(request):
                pass
        except urllib.error.HTTPError as error:
            if error.code == 404:
                raise NotionEnvironmentError(
                    "Database not found — check ARKMIND_NOTION_DATABASE_ID and share the "
                    "database with the integration (Database → Share → invite the "
                    "integration)"
                ) from error
            if error.code == 403:
                raise NotionEnvironmentError(
                    "Access denied — share the database with the integration "
                    "(Database → Share → invite the integration)"
                ) from error
            raise NotionEnvironmentError(f"Notion API error {error.code}") from error
        except urllib.error.URLError as error:
            raise NotionEnvironmentError(
                f"Network error while reaching Notion: {error.reason}"
            ) from error

    def create_page(
        self,
        title: str,
        content: str,
        *,
        book: str | None = None,
        author: str | None = None,
    ) -> str:
        """Create a page and return its id; ``content`` is Markdown, stored as Page Body blocks."""
        payload = json.dumps(self.build_page(title, content, book=book, author=author)).encode(
            "utf-8"
        )
        request = urllib.request.Request(_API_URL, data=payload, method="POST")
        request.add_header("Authorization", f"Bearer {self._token}")
        request.add_header("Notion-Version", _NOTION_VERSION)
        request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request) as response:
            page = json.loads(response.read())
        return page["id"]

    def fetch_page(self, page_id: str) -> dict[str, object]:
        """Return the raw page object (properties) for ``page_id``."""
        request = urllib.request.Request(_PAGE_URL.format(id=page_id), method="GET")
        request.add_header("Authorization", f"Bearer {self._token}")
        request.add_header("Notion-Version", _NOTION_VERSION)
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read())

    def fetch_children(self, page_id: str) -> list[dict[str, object]]:
        """Return the raw Page Body blocks of ``page_id``."""
        request = urllib.request.Request(_BLOCKS_URL.format(id=page_id), method="GET")
        request.add_header("Authorization", f"Bearer {self._token}")
        request.add_header("Notion-Version", _NOTION_VERSION)
        with urllib.request.urlopen(request) as response:
            payload = json.loads(response.read())
        return payload["results"]

    def build_page(
        self,
        title: str,
        content: str,
        *,
        book: str | None = None,
        author: str | None = None,
    ) -> dict[str, object]:
        """Map ``title`` / ``content`` onto a Notion ``pages.create`` request body.

        Properties carry management metadata only (frozen Editorial Database
        schema); the body goes to the Page Body ``children``.
        """
        return {
            "parent": {"database_id": self._database_id},
            "properties": {
                "Title": {"title": [{"text": {"content": title}}]},
                "Book": self._rich_text(book),
                "Author": self._rich_text(author),
                "Status": {"select": {"name": "Draft"}},
                "Word Count": {"number": word_count(content)},
            },
            "children": self._page_children(content),
        }

    @staticmethod
    def _page_children(content: str) -> list[dict[str, object]]:
        """Build the Page Body: the article first, then the editor/review footer."""

        def heading(name: str, level: int) -> dict[str, object]:
            block_type = f"heading_{level}"
            return {
                "object": "block",
                "type": block_type,
                block_type: {"rich_text": [{"type": "text", "text": {"content": name}}]},
            }

        divider: dict[str, object] = {"object": "block", "type": "divider", "divider": {}}
        return [
            *build_blocks(content),
            divider,
            heading(_EDITOR_HEADING, 2),
            divider,
            heading(_REVIEW_HEADING, 2),
        ]

    @staticmethod
    def _rich_text(text: str | None) -> dict[str, object]:
        """Return a rich_text property payload; empty when ``text`` is falsy."""
        if not text:
            return {"rich_text": []}
        return {"rich_text": [{"text": {"content": text}}]}


def word_count(markdown: str) -> int:
    """Approximate word count: ``markdown`` length with all whitespace removed.

    Markdown syntax characters still count — this is a cheap, deterministic
    size signal for the Word Count property, not a linguistic measure.
    """
    return len(_WHITESPACE.sub("", markdown))
