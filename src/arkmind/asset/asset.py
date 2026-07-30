"""Asset data model (Asset Contract v1).

Minimal frozen model: an Asset is a typed piece of content extracted from a
single Knowledge and belonging to a single book. ``asset_id`` is a UUID (v7,
assigned by the producer) rather than a content hash, because Assets may be
edited by hand later and their identity must survive content changes.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from arkmind.asset.asset_type import AssetType


class Asset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: str
    book_id: str
    knowledge_id: str
    type: AssetType
    content: str
    created_at: datetime
