"""SHA-256 checksum utility for the Source Registry (RFC-0001 v3)."""

from __future__ import annotations

import hashlib
from pathlib import Path

_CHUNK_SIZE = 65536


def calculate_sha256(file: Path) -> str:
    """Return the SHA-256 hex digest of ``file``."""
    digest = hashlib.sha256()
    with file.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()
