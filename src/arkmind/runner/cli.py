"""CLI entry point for the Dataset Runner (RFC-0008).

Parses a ``source_id`` argument, resolves it to ``sources/<source_id>/`` and
runs the DatasetRunner. No business logic lives here.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from arkmind.runner.dataset_runner import DatasetRunner

_SOURCES_ROOT = "sources"


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-run")
    parser.add_argument("source_id")
    args = parser.parse_args()
    DatasetRunner().run(Path(_SOURCES_ROOT) / args.source_id)
