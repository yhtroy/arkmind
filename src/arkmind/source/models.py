"""Source metadata model and lifecycle status (RFC-0001 v3)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class SourceStatus(str, Enum):
    """Source lifecycle status. Exactly three states (RFC-0001 v3)."""

    REGISTERED = "registered"
    CAPTURED = "captured"
    VERIFIED = "verified"


class SourceMetadata(BaseModel):
    """Frozen contract describing a registered Source.

    Persisted verbatim to ``sources/<id>/source.yaml`` as the single source of
    truth. Unknown fields are rejected (RFC-0001 v3).
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    origin: str
    version: str
    license: str
    checksum: str | None = None
    status: SourceStatus = SourceStatus.REGISTERED
    captured_at: datetime | None = None
    verified_at: datetime | None = None
