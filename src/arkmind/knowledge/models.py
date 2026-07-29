"""Knowledge data model (RFC-0004)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Knowledge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    knowledge_id: str
    fragment_id: str
    source_id: str
    text: str
    kind: str | None = None
    normalized: str | None = None
