"""DatasetResult model (RFC-0007)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from arkmind.fragment.models import Fragment
from arkmind.knowledge.models import Knowledge
from arkmind.provenance.models import Provenance


class DatasetResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    fragments: list[Fragment]
    knowledge: list[Knowledge]
    provenance: list[Provenance]
