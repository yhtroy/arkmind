"""CLI entry point for Notion environment bootstrap (M5.0.1).

Usage::

    arkmind-notion-check [--smoke]

Checks the Notion environment before the Writer ever runs: token validity,
database reachability/sharing, and (with ``--smoke``) a real write test that
creates ``Hello ArkMind v2`` and verifies the Editorial Database contract on
read-back: management properties (Status=Draft, Word Count, Book, Author) and
the Page Body template (content first, then the Editor Notes / Review footer).
Prints friendly per-step status instead of raw HTTP errors::

    OK Token
    OK Database (shared, read/write)
    OK Permission
    OK Created Notion Page
    OK Page ID: <id>
    OK Properties: Status=Draft Word Count=9
    OK Body: content first, then Editor Notes / Review
    OK Ready

Output is plain ASCII on purpose: the Windows console defaults to the GBK
codepage and would crash on non-ASCII glyphs (U+2713 etc.).

Credentials come from ``ARKMIND_NOTION_TOKEN`` / ``ARKMIND_NOTION_DATABASE_ID``.
No business logic lives here; the checks are delegated to
:class:`arkmind.notion.NotionClient`.
"""

from __future__ import annotations

import argparse
import io
import sys
import urllib.error
from typing import NoReturn

from arkmind.notion import MissingNotionConfigError, NotionClient, NotionEnvironmentError
from arkmind.notion.notion_client import word_count

_SMOKE_TITLE = "Hello ArkMind v2"
_SMOKE_CONTENT = "Smoke Test"
_SMOKE_BOOK = "Smoke Book"
_SMOKE_AUTHOR = "Smoke Author"
_FOOTER_HEADINGS = ("Editor Notes", "Review")
_FORBIDDEN_HEADINGS = ("AI Draft",)


def _fail(message: str) -> NoReturn:
    print(f"ERROR {message}", file=sys.stderr)
    raise SystemExit(1)


def _verify_smoke(page: dict[str, object], children: list[dict[str, object]]) -> None:
    """Check the created page against the Editorial Database contract."""
    properties = page["properties"]
    assert isinstance(properties, dict)
    title_payload = properties["Title"]
    status_payload = properties["Status"]
    count_payload = properties["Word Count"]
    book_payload = properties["Book"]
    author_payload = properties["Author"]
    assert isinstance(title_payload, dict) and isinstance(status_payload, dict)
    assert isinstance(count_payload, dict) and isinstance(book_payload, dict)
    assert isinstance(author_payload, dict)
    title = title_payload["title"]
    status = status_payload["select"]
    count = count_payload["number"]
    book = book_payload["rich_text"]
    author = author_payload["rich_text"]
    assert isinstance(title, list) and title
    assert isinstance(status, dict) and isinstance(count, int)
    assert isinstance(book, list) and isinstance(author, list)
    if title[0]["plain_text"] != _SMOKE_TITLE:
        _fail(f"Smoke verification failed: Title is {title[0]['plain_text']!r}")
    if status.get("name") != "Draft":
        _fail(f"Smoke verification failed: Status is {status.get('name')!r}, expected 'Draft'")
    if count != word_count(_SMOKE_CONTENT):
        _fail(
            f"Smoke verification failed: Word Count is {count}, expected {word_count(_SMOKE_CONTENT)}"
        )
    if not book or book[0]["plain_text"] != _SMOKE_BOOK:
        _fail("Smoke verification failed: Book property is empty or wrong")
    if not author or author[0]["plain_text"] != _SMOKE_AUTHOR:
        _fail("Smoke verification failed: Author property is empty or wrong")
    headings = set()
    for block in children:
        block_type = block["type"]
        assert isinstance(block_type, str)
        if not block_type.startswith("heading_"):
            continue
        heading_payload = block[block_type]
        assert isinstance(heading_payload, dict)
        rich_text = heading_payload["rich_text"]
        assert isinstance(rich_text, list) and rich_text
        first = rich_text[0]
        assert isinstance(first, dict)
        plain_text = first["plain_text"]
        assert isinstance(plain_text, str)
        headings.add(plain_text)
    missing = [name for name in _FOOTER_HEADINGS if name not in headings]
    if missing:
        _fail(f"Smoke verification failed: Page Body missing headings {missing}")
    forbidden = [name for name in _FORBIDDEN_HEADINGS if name in headings]
    if forbidden:
        _fail(f"Smoke verification failed: unexpected headings in Page Body {forbidden}")
    if not children or children[0]["type"] != "paragraph":
        _fail("Smoke verification failed: Page Body must start with the article content")
    first_rich_text = children[0]["paragraph"]
    assert isinstance(first_rich_text, dict)
    rich_text = first_rich_text["rich_text"]
    assert isinstance(rich_text, list) and rich_text
    first_text = rich_text[0]
    assert isinstance(first_text, dict)
    plain_text = first_text["plain_text"]
    assert isinstance(plain_text, str)
    if plain_text != _SMOKE_CONTENT:
        _fail(
            f"Smoke verification failed: first block is {plain_text!r}, expected the article content"
        )


def main() -> None:
    # Windows console defaults to GBK; never crash on non-encodable output.
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="replace")

    parser = argparse.ArgumentParser(prog="arkmind-notion-check")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="run a real write test ('Hello ArkMind v2') and verify the page on read-back",
    )
    args = parser.parse_args()

    try:
        client = NotionClient.from_env()
    except MissingNotionConfigError as error:
        _fail(f"{error} — set ARKMIND_NOTION_TOKEN and ARKMIND_NOTION_DATABASE_ID first")

    try:
        client.verify_token()
    except NotionEnvironmentError as error:
        _fail(str(error))
    print("OK Token")

    try:
        client.verify_database()
    except NotionEnvironmentError as error:
        _fail(str(error))
    print("OK Database (shared, read/write)")
    print("OK Permission")

    if args.smoke:
        print(f'Smoke test: creating page "{_SMOKE_TITLE}" ...')
        try:
            page_id = client.create_page(
                title=_SMOKE_TITLE,
                content=_SMOKE_CONTENT,
                book=_SMOKE_BOOK,
                author=_SMOKE_AUTHOR,
            )
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            _fail(f"Smoke test failed: HTTP {error.code} — {body}")
        except NotionEnvironmentError as error:
            _fail(f"Smoke test failed: {error}")
        print("OK Created Notion Page")
        print(f"OK Page ID: {page_id}")
        try:
            page = client.fetch_page(page_id)
            children = client.fetch_children(page_id)
        except urllib.error.HTTPError as error:
            _fail(f"Smoke verification failed: HTTP {error.code}")
        _verify_smoke(page, children)
        print(f"OK Properties: Status=Draft Word Count={word_count(_SMOKE_CONTENT)}")
        print("OK Body: content first, then Editor Notes / Review")

    print("OK Ready")


if __name__ == "__main__":
    main()
