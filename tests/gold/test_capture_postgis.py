"""Gold Sample capture validation for Dataset-0001 (PostGIS 3.6) — RFC-0009.

Validates the frozen Source registered under ``sources/postgis-3.6-en``:
``original`` exists, its checksum is recorded, integrity re-verifies, and the
lifecycle status is ``verified``. The frozen ``original`` is kept local (it is
git-ignored), so these tests exercise the on-disk Gold Sample.
"""

from __future__ import annotations

from pathlib import Path

from arkmind.source.checksum import calculate_sha256
from arkmind.source.models import SourceStatus
from arkmind.source.registry import SourceRegistry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SOURCES_ROOT = _REPO_ROOT / "sources"
_SOURCE_ID = "postgis-3.6-en"
_SOURCE_DIR = _SOURCES_ROOT / _SOURCE_ID


def test_original_exists() -> None:
    assert (_SOURCE_DIR / "original").is_file()


def test_checksum_not_empty() -> None:
    metadata = SourceRegistry(_SOURCES_ROOT)._load(_SOURCE_ID)
    assert metadata.checksum


def test_verify_succeeds() -> None:
    metadata = SourceRegistry(_SOURCES_ROOT)._load(_SOURCE_ID)
    assert calculate_sha256(_SOURCE_DIR / "original") == metadata.checksum


def test_status_verified() -> None:
    metadata = SourceRegistry(_SOURCES_ROOT)._load(_SOURCE_ID)
    assert metadata.status is SourceStatus.VERIFIED
