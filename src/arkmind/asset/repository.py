"""In-memory Asset repository (Asset Contract v1).

Provides exactly the operations frozen by the contract: ``add`` / ``get`` /
``list`` / ``list_by_book``. Assets are held in memory keyed by ``asset_id``;
persistence to disk is a separate concern (dataset export), so this repository
does not touch the filesystem.
"""

from __future__ import annotations

import builtins

from arkmind.asset.asset import Asset


class AssetRepository:
    """Hold Assets in memory, keyed by ``asset_id``."""

    def __init__(self) -> None:
        self._assets: dict[str, Asset] = {}

    def add(self, asset: Asset) -> None:
        self._assets[asset.asset_id] = asset

    def get(self, asset_id: str) -> Asset | None:
        return self._assets.get(asset_id)

    def list(self) -> builtins.list[Asset]:
        return list(self._assets.values())

    def list_by_book(self, book_id: str) -> builtins.list[Asset]:
        return [asset for asset in self._assets.values() if asset.book_id == book_id]
