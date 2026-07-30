"""Tests for AssetRepository (Asset Contract v1)."""

from __future__ import annotations

from datetime import UTC, datetime

from arkmind.asset import Asset, AssetRepository, AssetType


def _asset(asset_id: str, book_id: str) -> Asset:
    return Asset(
        asset_id=asset_id,
        book_id=book_id,
        knowledge_id=f"k-{asset_id}",
        type=AssetType.CONCEPT,
        content=f"content-{asset_id}",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_add_and_get() -> None:
    repo = AssetRepository()
    asset = _asset("a1", "book-1")
    repo.add(asset)
    assert repo.get("a1") == asset


def test_get_missing_returns_none() -> None:
    assert AssetRepository().get("nope") is None


def test_list_returns_all() -> None:
    repo = AssetRepository()
    repo.add(_asset("a1", "book-1"))
    repo.add(_asset("a2", "book-2"))
    assert {a.asset_id for a in repo.list()} == {"a1", "a2"}


def test_list_by_book_filters() -> None:
    repo = AssetRepository()
    repo.add(_asset("a1", "book-1"))
    repo.add(_asset("a2", "book-1"))
    repo.add(_asset("a3", "book-2"))
    assert {a.asset_id for a in repo.list_by_book("book-1")} == {"a1", "a2"}
    assert [a.asset_id for a in repo.list_by_book("book-2")] == ["a3"]


def test_list_by_book_empty_when_unknown() -> None:
    repo = AssetRepository()
    repo.add(_asset("a1", "book-1"))
    assert repo.list_by_book("book-x") == []


def test_add_same_id_overwrites() -> None:
    repo = AssetRepository()
    repo.add(_asset("a1", "book-1"))
    repo.add(_asset("a1", "book-2"))
    assert repo.get("a1").book_id == "book-2"
    assert len(repo.list()) == 1
