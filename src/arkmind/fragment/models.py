"""Fragment data model (RFC-0003)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Fragment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fragment_id: str
    page_number: int
    sequence: int
    text: str
