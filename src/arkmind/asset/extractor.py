"""AssetExtractor — extract typed Assets from Knowledge (Asset Contract v1).

Stub stage: the deterministic rules for CONCEPT / DEFINITION / QUOTE arrive in a
later task. For now ``extract`` returns an empty list so the asset CLI has a
stable seam to call. No AI; deterministic; does not modify Knowledge.
"""

from __future__ import annotations

from arkmind.asset.asset import Asset
from arkmind.knowledge.models import Knowledge


class AssetExtractor:
    """Turn Knowledge into Assets. Currently a no-op that produces no assets."""

    def extract(self, knowledge: list[Knowledge]) -> list[Asset]:
        return []
