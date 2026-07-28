"""Tests for FragmentExtractor (RFC-0003)."""

from __future__ import annotations

import hashlib

from arkmind.fragment.extractor import FragmentExtractor
from arkmind.fragment.models import Fragment

_SOURCE_ID = "dataset-0001"


def _expected_id(page_number: int, sequence: int, text: str) -> str:
    payload = f"{_SOURCE_ID}\n{page_number}\n{sequence}\n{text}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_single_page_single_paragraph() -> None:
    result = FragmentExtractor().extract(["Hello world"], _SOURCE_ID)
    assert len(result) == 1
    fragment = result[0]
    assert isinstance(fragment, Fragment)
    assert fragment.page_number == 1
    assert fragment.sequence == 0
    assert fragment.text == "Hello world"


def test_single_page_multiple_paragraphs() -> None:
    result = FragmentExtractor().extract(["A\n\nB\n\nC"], _SOURCE_ID)
    assert [f.text for f in result] == ["A", "B", "C"]
    assert [f.sequence for f in result] == [0, 1, 2]
    assert all(f.page_number == 1 for f in result)


def test_multiple_pages() -> None:
    result = FragmentExtractor().extract(["First page", "Second page"], _SOURCE_ID)
    assert [(f.page_number, f.sequence, f.text) for f in result] == [
        (1, 0, "First page"),
        (2, 1, "Second page"),
    ]


def test_consecutive_blank_lines_collapse() -> None:
    result = FragmentExtractor().extract(["A\n\n\n\n\nB"], _SOURCE_ID)
    assert [f.text for f in result] == ["A", "B"]
    assert [f.sequence for f in result] == [0, 1]


def test_empty_and_whitespace_pages_produce_nothing() -> None:
    result = FragmentExtractor().extract(["", "   \n  \n\t", "Real text"], _SOURCE_ID)
    assert len(result) == 1
    assert result[0].page_number == 3
    assert result[0].text == "Real text"


def test_fragment_id_is_stable_and_matches_algorithm() -> None:
    pages = ["Alpha\n\nBeta", "Gamma"]
    first = FragmentExtractor().extract(pages, _SOURCE_ID)
    second = FragmentExtractor().extract(pages, _SOURCE_ID)
    assert [f.fragment_id for f in first] == [f.fragment_id for f in second]
    assert first[0].fragment_id == _expected_id(1, 0, "Alpha")
    assert first[1].fragment_id == _expected_id(1, 1, "Beta")
    assert first[2].fragment_id == _expected_id(2, 2, "Gamma")


def test_document_order_preserved() -> None:
    pages = ["P1a\n\nP1b", "P2a\n\nP2b"]
    result = FragmentExtractor().extract(pages, _SOURCE_ID)
    assert [(f.page_number, f.sequence, f.text) for f in result] == [
        (1, 0, "P1a"),
        (1, 1, "P1b"),
        (2, 2, "P2a"),
        (2, 3, "P2b"),
    ]
