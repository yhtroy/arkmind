"""Tests for the Asset model and AssetType (Asset Contract v1)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from arkmind.asset import Asset, AssetType


def _asset(asset_id: str = "a1", book_id: str = "book-1") -> Asset:
    return Asset(
        asset_id=asset_id,
        book_id=book_id,
        knowledge_id="k1",
        type=AssetType.CONCEPT,
        content="long-term thinking",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_asset_type_values() -> None:
    assert [t.value for t in AssetType] == ["CONCEPT", "DEFINITION", "QUOTE"]


def test_asset_holds_all_fields() -> None:
    asset = _asset()
    assert asset.asset_id == "a1"
    assert asset.book_id == "book-1"
    assert asset.knowledge_id == "k1"
    assert asset.type is AssetType.CONCEPT
    assert asset.content == "long-term thinking"
    assert asset.created_at == datetime(2026, 1, 1, tzinfo=UTC)


def test_asset_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Asset(
            asset_id="a1",
            book_id="book-1",
            knowledge_id="k1",
            type=AssetType.QUOTE,
            content="c",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            score=1.0,
        )


def test_asset_requires_all_fields() -> None:
    with pytest.raises(ValidationError):
        Asset(asset_id="a1", book_id="book-1")
