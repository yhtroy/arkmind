"""AssetExtractor — turn Knowledge into typed Assets (Asset Contract v1).

For each Knowledge, run one prompt per AssetType (CONCEPT / DEFINITION / QUOTE)
through the injected LLMClient. Each non-empty response becomes one Asset; a
whitespace-only response produces no Asset — so one Knowledge yields at most
three Assets. Pure orchestration: prompt bodies live in files loaded by
PromptLoader and the model call is delegated to LLMClient; this module never
reads a prompt file nor talks to a model directly.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from arkmind.asset.asset import Asset
from arkmind.asset.asset_type import AssetType
from arkmind.knowledge.models import Knowledge
from arkmind.runtime import LLMClient, PromptLoader


class AssetExtractor:
    """Orchestrate PromptLoader + LLMClient to extract Assets from Knowledge."""

    def __init__(self, loader: PromptLoader, llm: LLMClient) -> None:
        self._loader = loader
        self._llm = llm

    def extract(self, knowledge: list[Knowledge]) -> list[Asset]:
        assets: list[Asset] = []
        for item in knowledge:
            for asset_type in AssetType:
                prompt = self._loader.load(f"asset/{asset_type.value.lower()}")
                response = self._llm.generate(prompt, item.text)
                if response.strip() == "":
                    continue
                assets.append(
                    Asset(
                        asset_id=str(uuid4()),
                        book_id=item.source_id,
                        knowledge_id=item.knowledge_id,
                        type=asset_type,
                        content=response,
                        created_at=datetime.now(UTC),
                    )
                )
        return assets
