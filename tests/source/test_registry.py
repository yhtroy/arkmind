"""Tests for SourceRegistry lifecycle (RFC-0001 v3, Definition of Done)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from arkmind.source.checksum import calculate_sha256
from arkmind.source.exceptions import (
    ChecksumMismatchError,
    InvalidStatusError,
    SourceNotFoundError,
)
from arkmind.source.models import SourceMetadata, SourceStatus
from arkmind.source.registry import SourceRegistry

_SOURCE_ID = "dataset-0001"


def _metadata(source_id: str = _SOURCE_ID) -> SourceMetadata:
    return SourceMetadata(
        id=source_id,
        title="Example Source",
        origin="https://example.org/doc",
        version="1.0.0",
        license="public-domain",
    )


def test_register_creates_yaml_at_registered(tmp_path: Path) -> None:
    registry = SourceRegistry(tmp_path)
    result = registry.register(_metadata())
    assert result.status is SourceStatus.REGISTERED
    assert result.checksum is None
    assert (tmp_path / _SOURCE_ID / "source.yaml").is_file()


def test_capture_freezes_original_and_sets_checksum(tmp_path: Path) -> None:
    registry = SourceRegistry(tmp_path)
    registry.register(_metadata())
    raw = tmp_path / "raw.txt"
    raw.write_bytes(b"hello arkmind")
    result = registry.capture(_SOURCE_ID, raw)
    original = tmp_path / _SOURCE_ID / "original"
    assert original.is_file()
    assert result.status is SourceStatus.CAPTURED
    assert result.checksum == calculate_sha256(raw)
    assert result.captured_at is not None


def test_verify_succeeds_when_frozen_copy_matches(tmp_path: Path) -> None:
    registry = SourceRegistry(tmp_path)
    registry.register(_metadata())
    raw = tmp_path / "raw.txt"
    raw.write_bytes(b"hello arkmind")
    registry.capture(_SOURCE_ID, raw)
    result = registry.verify(_SOURCE_ID)
    assert result.status is SourceStatus.VERIFIED
    assert result.verified_at is not None


def test_verify_detects_tampered_original(tmp_path: Path) -> None:
    registry = SourceRegistry(tmp_path)
    registry.register(_metadata())
    raw = tmp_path / "raw.txt"
    raw.write_bytes(b"hello arkmind")
    registry.capture(_SOURCE_ID, raw)
    (tmp_path / _SOURCE_ID / "original").write_bytes(b"tampered")
    with pytest.raises(ChecksumMismatchError):
        registry.verify(_SOURCE_ID)


def test_capture_requires_registered_status(tmp_path: Path) -> None:
    registry = SourceRegistry(tmp_path)
    registry.register(_metadata())
    raw = tmp_path / "raw.txt"
    raw.write_bytes(b"data")
    registry.capture(_SOURCE_ID, raw)
    with pytest.raises(InvalidStatusError):
        registry.capture(_SOURCE_ID, raw)


def test_verify_requires_captured_status(tmp_path: Path) -> None:
    registry = SourceRegistry(tmp_path)
    registry.register(_metadata())
    with pytest.raises(InvalidStatusError):
        registry.verify(_SOURCE_ID)


def test_missing_source_raises(tmp_path: Path) -> None:
    registry = SourceRegistry(tmp_path)
    with pytest.raises(SourceNotFoundError):
        registry.verify("does-not-exist")


def test_unknown_field_rejected() -> None:
    with pytest.raises(ValidationError):
        SourceMetadata.model_validate(
            {
                "id": "x",
                "title": "t",
                "origin": "o",
                "version": "v",
                "license": "l",
                "publisher": "should-be-rejected",
            }
        )


def test_yaml_roundtrip_is_stable(tmp_path: Path) -> None:
    registry = SourceRegistry(tmp_path)
    registry.register(_metadata())
    raw = tmp_path / "raw.txt"
    raw.write_bytes(b"roundtrip")
    captured = registry.capture(_SOURCE_ID, raw)
    loaded = yaml.safe_load((tmp_path / _SOURCE_ID / "source.yaml").read_text(encoding="utf-8"))
    assert SourceMetadata.model_validate(loaded) == captured
