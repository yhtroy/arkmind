"""Exceptions for the Source Registry (RFC-0001 v3). Exactly three."""

from __future__ import annotations


class SourceNotFoundError(Exception):
    """Raised when a source id has no registered ``source.yaml`` (or frozen copy)."""


class InvalidStatusError(Exception):
    """Raised on an illegal lifecycle transition."""


class ChecksumMismatchError(Exception):
    """Raised when a recomputed checksum does not match the stored value."""
