"""CLI entry point for Notion environment bootstrap (M5.0.1).

Usage::

    arkmind-notion-check [--smoke]

Checks the Notion environment before the Writer ever runs: token validity,
database reachability/sharing, and (with ``--smoke``) a real ``create_page``
write test. Prints friendly per-step status instead of raw HTTP errors:

    ✓ Token OK
    ✓ Database OK (shared, read/write)
    ✓ Permission OK
    ✓ Ready

Credentials come from ``ARKMIND_NOTION_TOKEN`` / ``ARKMIND_NOTION_DATABASE_ID``.
No business logic lives here; the checks are delegated to
:class:`arkmind.notion.NotionClient`.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
from typing import NoReturn

from arkmind.notion import MissingNotionConfigError, NotionClient, NotionEnvironmentError


def _fail(message: str) -> NoReturn:
    print(f"✗ {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
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
    print("✓ Token OK")

    try:
        client.verify_database()
    except NotionEnvironmentError as error:
        _fail(str(error))
    print("✓ Database OK (shared, read/write)")
    print("✓ Permission OK")

    if args.smoke:
        print('→ Smoke test: creating page "Hello ArkMind" ...')
        try:
            page_id = client.create_page(title="Hello ArkMind", content="Smoke Test")
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            _fail(f"Smoke test failed: HTTP {error.code} — {body}")
        except NotionEnvironmentError as error:
            _fail(f"Smoke test failed: {error}")
        print("✓ Created Notion Page")
        print(f"✓ Page ID: {page_id}")

    print("✓ Ready")


if __name__ == "__main__":
    main()
