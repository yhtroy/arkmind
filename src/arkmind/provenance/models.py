"""Provenance data model (RFC-0006)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    knowledge_id: str
    fragment_id: str
    source_id: str
