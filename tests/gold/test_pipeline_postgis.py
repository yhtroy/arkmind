"""Gold Sample pipeline validation for Dataset-0001 (PostGIS 3.6) — RFC-0010.

Runs the full Dataset Pipeline through the ``arkmind-run`` CLI against the frozen
Source ``sources/postgis-3.6-en`` and asserts the M1 output contract: the three
JSON artifacts exist, counts are positive and consistent, samples are well-formed
and traceable, ids are globally unique, and — most importantly — two consecutive
runs are byte-for-byte identical (deterministic output).

The frozen ``original`` is kept local (git-ignored), so these tests exercise the
on-disk Gold Sample and require it to be present and ``verified``.
"""

from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path
from typing import Any

import pytest

from arkmind.runner import cli
from arkmind.source.models import SourceStatus
from arkmind.source.registry import SourceRegistry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SOURCES_ROOT = _REPO_ROOT / "sources"
_SOURCE_ID = "postgis-3.6-en"
_SOURCE_DIR = _SOURCES_ROOT / _SOURCE_ID
_OUTPUT_DIR = _SOURCE_DIR / "output"
_FILES = ("knowledge.json", "provenance.json", "summary.json")
_SAMPLE_SIZE = 20
_SEED = 20260727


def _invoke_cli() -> None:
    """Run ``arkmind-run postgis-3.6-en`` exactly as the console-script would."""
    old_argv = sys.argv
    old_cwd = Path.cwd()
    os.chdir(_REPO_ROOT)
    sys.argv = ["arkmind-run", _SOURCE_ID]
    try:
        cli.main()
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)


def _load(name: str) -> Any:
    return json.loads((_OUTPUT_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def outputs() -> dict[str, Any]:
    _invoke_cli()
    return {
        "knowledge": _load("knowledge.json"),
        "provenance": _load("provenance.json"),
        "summary": _load("summary.json"),
    }


def test_dataset_is_verified() -> None:
    metadata = SourceRegistry(_SOURCES_ROOT)._load(_SOURCE_ID)
    assert metadata.status is SourceStatus.VERIFIED


def test_1_runner_completes(outputs: dict[str, Any]) -> None:
    assert _OUTPUT_DIR.is_dir()


def test_2_three_output_files_exist(outputs: dict[str, Any]) -> None:
    for name in _FILES:
        assert (_OUTPUT_DIR / name).is_file()


def test_3_summary_counts_positive(outputs: dict[str, Any]) -> None:
    summary = outputs["summary"]
    assert summary["fragments"] > 0
    assert summary["knowledge"] > 0
    assert summary["provenance"] > 0


def test_4_knowledge_equals_provenance(outputs: dict[str, Any]) -> None:
    assert len(outputs["knowledge"]) == len(outputs["provenance"])
    assert outputs["summary"]["knowledge"] == outputs["summary"]["provenance"]


def test_5_knowledge_sample_wellformed(outputs: dict[str, Any]) -> None:
    knowledge = outputs["knowledge"]
    provenance_by_kid = {p["knowledge_id"]: p for p in outputs["provenance"]}
    rng = random.Random(_SEED)
    sample = rng.sample(knowledge, min(_SAMPLE_SIZE, len(knowledge)))
    assert len(sample) >= _SAMPLE_SIZE
    for item in sample:
        assert item["text"]
        assert item["kind"]
        assert item["source_id"] == _SOURCE_ID
        # fragment_id is traceable: the matching provenance shares the same fragment_id.
        assert item["fragment_id"]
        prov = provenance_by_kid[item["knowledge_id"]]
        assert prov["fragment_id"] == item["fragment_id"]


def test_6_provenance_sample_wellformed(outputs: dict[str, Any]) -> None:
    provenance = outputs["provenance"]
    rng = random.Random(_SEED)
    sample = rng.sample(provenance, min(_SAMPLE_SIZE, len(provenance)))
    assert len(sample) >= _SAMPLE_SIZE
    for item in sample:
        assert item["knowledge_id"]
        assert item["fragment_id"]
        assert item["source_id"]


def test_7_knowledge_id_globally_unique(outputs: dict[str, Any]) -> None:
    ids = [k["knowledge_id"] for k in outputs["knowledge"]]
    assert len(set(ids)) == len(ids)


def test_8_fragment_id_globally_unique(outputs: dict[str, Any]) -> None:
    ids = [k["fragment_id"] for k in outputs["knowledge"]]
    assert len(set(ids)) == len(ids)


def test_9_output_is_byte_identical_across_runs() -> None:
    _invoke_cli()
    first = {name: (_OUTPUT_DIR / name).read_bytes() for name in _FILES}
    _invoke_cli()
    second = {name: (_OUTPUT_DIR / name).read_bytes() for name in _FILES}
    for name in _FILES:
        assert first[name] == second[name]
