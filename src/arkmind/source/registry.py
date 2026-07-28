"""Source Registry — register / capture / verify (RFC-0001 v3).

Repository layout (fixed)::

    sources/
        <source-id>/
            source.yaml   # single source of truth (SSOT)
            original      # frozen raw bytes (no extension)

The registry only knows ``source.yaml`` and ``original``. File types (PDF, HTML,
Markdown, ...) belong to future SourceProviders, not to the registry.
"""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import yaml

from arkmind.source.checksum import calculate_sha256
from arkmind.source.exceptions import (
    ChecksumMismatchError,
    InvalidStatusError,
    SourceNotFoundError,
)
from arkmind.source.models import SourceMetadata, SourceStatus

_YAML_NAME = "source.yaml"
_ORIGINAL_NAME = "original"


class SourceRegistry:
    """Persist and manage the lifecycle of Sources under a fixed root."""

    def __init__(self, root: Path) -> None:
        self._root = Path(root)

    def _dir(self, source_id: str) -> Path:
        return self._root / source_id

    def _yaml_path(self, source_id: str) -> Path:
        return self._dir(source_id) / _YAML_NAME

    def _original_path(self, source_id: str) -> Path:
        return self._dir(source_id) / _ORIGINAL_NAME

    def _load(self, source_id: str) -> SourceMetadata:
        path = self._yaml_path(source_id)
        if not path.is_file():
            raise SourceNotFoundError(source_id)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return SourceMetadata.model_validate(data)

    def _save(self, metadata: SourceMetadata) -> None:
        path = self._yaml_path(metadata.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = metadata.model_dump(mode="json")
        path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def register(self, metadata: SourceMetadata) -> SourceMetadata:
        """Persist a new Source at status ``registered``.

        The registry does not infer metadata; it only saves what the caller
        (Product / Dataset) provides, normalised to the initial lifecycle state.
        """
        record = metadata.model_copy(
            update={
                "status": SourceStatus.REGISTERED,
                "checksum": None,
                "captured_at": None,
                "verified_at": None,
            }
        )
        self._save(record)
        return record

    def capture(self, source_id: str, file_path: Path) -> SourceMetadata:
        """Freeze the original file, compute its checksum, move to ``captured``."""
        metadata = self._load(source_id)
        if metadata.status is not SourceStatus.REGISTERED:
            raise InvalidStatusError(
                f"{source_id}: cannot capture from status {metadata.status.value}"
            )
        original = self._original_path(source_id)
        shutil.copyfile(file_path, original)
        record = metadata.model_copy(
            update={
                "checksum": calculate_sha256(original),
                "captured_at": datetime.now(UTC),
                "status": SourceStatus.CAPTURED,
            }
        )
        self._save(record)
        return record

    def verify(self, source_id: str) -> SourceMetadata:
        """Recompute the checksum of the frozen copy and move to ``verified``."""
        metadata = self._load(source_id)
        if metadata.status is not SourceStatus.CAPTURED:
            raise InvalidStatusError(
                f"{source_id}: cannot verify from status {metadata.status.value}"
            )
        original = self._original_path(source_id)
        if not original.is_file():
            raise SourceNotFoundError(f"{source_id}: frozen original missing")
        if calculate_sha256(original) != metadata.checksum:
            raise ChecksumMismatchError(source_id)
        record = metadata.model_copy(
            update={
                "status": SourceStatus.VERIFIED,
                "verified_at": datetime.now(UTC),
            }
        )
        self._save(record)
        return record
