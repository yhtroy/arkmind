"""CLI entry point for Notion environment bootstrap (M5.0.1).

Usage::

    arkmind-notion-check [--smoke]

Checks the Notion environment before the Writer ever runs: token validity,
database reachability/sharing, and (with ``--smoke``) a real ``create_page``
write test. Prints friendly per-step status instead of raw HTTP errors:

    OK Token
    OK Database (shared, read/write)
    OK Permission
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


def _fail(message: str) -> NoReturn:
    print(f"ERROR {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    # Windows console defaults to GBK; never crash on non-encodable output.
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="replace")

    parser = argparse.ArgumentParser(prog="arkmind-notion-check")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="run a real create_page write test ('Hello ArkMind')",
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
        print('Smoke test: creating page "Hello ArkMind" ...')
        try:
            page_id = client.create_page(title="Hello ArkMind", content="Smoke Test")
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            _fail(f"Smoke test failed: HTTP {error.code} — {body}")
        except NotionEnvironmentError as error:
            _fail(f"Smoke test failed: {error}")
        print("OK Created Notion Page")
        print(f"OK Page ID: {page_id}")

    print("OK Ready")


if __name__ == "__main__":
    main()
