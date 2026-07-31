"""Resolve a Topic's asset_id references to full Asset content (M3 Task-002).

Topic stays Reference Only: it stores asset_id lists, and the source of truth for
the text lives in the Asset Repository. The Writer resolves those references at
runtime — it never copies content into the Topic. ``resolve`` performs a plain
lookup and returns the full Concept / Definition / Quote bodies unchanged: no
summarising, rewriting or deletion. A dangling asset_id (absent from the
repository) is skipped rather than fabricated.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from arkmind.asset import AssetRepository
from arkmind.topic import Topic


@dataclass(frozen=True)
class ResolvedTopic:
    """A Topic with its asset_id references expanded to full Asset content."""

    title: str
    concepts: list[str] = field(default_factory=list)
    definitions: list[str] = field(default_factory=list)
    quotes: list[str] = field(default_factory=list)


class AssetResolver:
    """Look up a Topic's asset_id references in the Asset Repository."""

    def resolve(self, topic: Topic, assets: AssetRepository) -> ResolvedTopic:
        return ResolvedTopic(
            title=topic.title,
            concepts=self._contents(topic.concepts, assets),
            definitions=self._contents(topic.definitions, assets),
            quotes=self._contents(topic.quotes, assets),
        )

    def _contents(self, asset_ids: list[str], assets: AssetRepository) -> list[str]:
        contents: list[str] = []
        for asset_id in asset_ids:
            asset = assets.get(asset_id)
            if asset is not None:
                contents.append(asset.content)
        return contents
