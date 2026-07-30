"""Exceptions for the AI Runtime (Runtime Contract v1)."""

from __future__ import annotations


class PromptNotFoundError(Exception):
    """Raised when a requested prompt file does not exist."""
