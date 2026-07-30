"""Model configuration for the AI Runtime (Runtime Contract v1).

Frozen v1 fields: ``model`` and ``temperature`` only. ``temperature`` defaults
to 0 for stable, repeatable output. New knobs (max_tokens, top_p, seed,
timeout) are added by amending the contract, not pre-allocated here.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str
    temperature: float = 0.0
