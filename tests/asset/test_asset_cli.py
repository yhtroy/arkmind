"""Tests for the arkmind-asset CLI (TASK-002.5, wired in TASK-004).

These exercise the full chain: read Knowledge -> PromptLoader (real prompts/) ->
FakeLLMClient -> Asset -> asset.json. FakeLLMClient echoes the Knowledge text, so
each Knowledge produces one Asset per type.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arkmind.asset import asset_cli
from arkmind.asset.asset_cli import _build_llm
from arkmind.runtime import FakeLLMClient, OpenAICompatibleClient


def _knowledge_item(knowledge_id: str = "k1") -> dict[str, object]:
    return {
        "knowledge_id": knowledge_id,
        "fragment_id": "f1",
        "source_id": "book-1",
        "text": "long-term thinking",
    }


def test_main_reads_knowledge_and_writes_typed_assets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "asset.json"
    input_path.write_text(json.dumps([_knowledge_item()]), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["arkmind-asset", str(input_path), str(output_path)])
    asset_cli.main()

    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert {r["type"] for r in result} == {"CONCEPT", "DEFINITION", "QUOTE"}
    assert all(r["content"] == "long-term thinking" for r in result)
    assert all(r["book_id"] == "book-1" for r in result)


def test_main_handles_empty_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "asset.json"
    input_path.write_text(json.dumps([]), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["arkmind-asset", str(input_path), str(output_path)])
    asset_cli.main()

    assert json.loads(output_path.read_text(encoding="utf-8")) == []


def test_build_llm_defaults_to_fake() -> None:
    assert isinstance(_build_llm("fake", None), FakeLLMClient)


def test_build_llm_real_requires_model() -> None:
    with pytest.raises(SystemExit):
        _build_llm("real", None)


def test_build_llm_real_builds_openai_compatible(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARKMIND_LLM_API_KEY", "sk-test")
    monkeypatch.delenv("ARKMIND_LLM_BASE_URL", raising=False)
    assert isinstance(_build_llm("real", "gpt-x"), OpenAICompatibleClient)
