"""Tests for calculate_sha256 (RFC-0001 v3)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from arkmind.source.checksum import calculate_sha256


def test_same_content_same_hash(tmp_path: Path) -> None:
    content = b"ArkMind source bytes"
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(content)
    b.write_bytes(content)
    assert calculate_sha256(a) == calculate_sha256(b)


def test_hash_matches_hashlib(tmp_path: Path) -> None:
    content = b"deterministic"
    f = tmp_path / "f.bin"
    f.write_bytes(content)
    assert calculate_sha256(f) == hashlib.sha256(content).hexdigest()


def test_modified_content_changes_hash(tmp_path: Path) -> None:
    f = tmp_path / "f.bin"
    f.write_bytes(b"original")
    before = calculate_sha256(f)
    f.write_bytes(b"tampered")
    after = calculate_sha256(f)
    assert before != after
