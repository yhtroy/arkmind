"""Tests for the WriterService runtime wiring (M3 Task-003, M5 Task-003).

Exercise the chain Topic -> PromptBuilder -> LLMClient.generate ->
NotionClient.create_page -> page id using only offline clients. No API key,
network or vendor SDK is touched.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from arkmind.asset import Asset, AssetRepository, AssetType
from arkmind.notion import MissingNotionConfigError
from arkmind.runtime import FakeLLMClient, LLMClient
from arkmind.topic import Topic
from arkmind.writer import WriterService


class _RecordingLLM(LLMClient):
    """Offline client that records the (prompt, text) it received."""

    def __init__(self, response: str) -> None:
        self.prompt: str | None = None
        self.text: str | None = None
        self._response = response

    def generate(self, prompt: str, text: str) -> str:
        self.prompt = prompt
        self.text = text
        return self._response


class _RecordingNotion:
    """Offline stand-in for NotionClient — records without any network."""

    def __init__(self, page_id: str = "page_001") -> None:
        self.page_id = page_id
        self.stored: list[tuple[str, str]] = []

    def create_page(self, title: str, content: str) -> str:
        self.stored.append((title, content))
        return self.page_id


def _repo(*assets: Asset) -> AssetRepository:
    repo = AssetRepository()
    for asset in assets:
        repo.add(asset)
    return repo


def _asset(asset_id: str, asset_type: AssetType, content: str) -> Asset:
    return Asset(
        asset_id=asset_id,
        book_id="b1",
        knowledge_id="k1",
        type=asset_type,
        content=content,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _topic() -> Topic:
    return Topic(
        topic_id="topic-001",
        title="黑天鹅",
        concepts=["c1"],
        definitions=[],
        quotes=[],
    )


def test_write_stores_content_in_notion_and_returns_page_id() -> None:
    repo = _repo(_asset("c1", AssetType.CONCEPT, "极不可能却影响巨大的事件"))
    llm = _RecordingLLM("# 假标题\n\n正文")
    notion = _RecordingNotion(page_id="page_abc")

    page_id = WriterService(llm=llm, notion=notion).write([_topic()], repo)

    # The page id comes back from Notion; content is the model response verbatim,
    # and the title is taken from the document's level-1 heading.
    assert page_id == "page_abc"
    assert notion.stored == [("假标题", "# 假标题\n\n正文")]


def test_write_passes_instruction_as_prompt_and_context_as_text() -> None:
    repo = _repo(_asset("c1", AssetType.CONCEPT, "极不可能却影响巨大的事件"))
    llm = _RecordingLLM("# 标题\n\n正文")

    WriterService(llm=llm, notion=_RecordingNotion()).write([_topic()], repo)

    # prompt = externalised writer instruction (system); text = Topic Context (user).
    assert llm.prompt is not None and "博" in llm.prompt
    assert llm.text is not None
    assert "黑天鹅" in llm.text
    assert "极不可能却影响巨大的事件" in llm.text


def test_write_with_fake_llm_stores_verbatim() -> None:
    repo = _repo(_asset("c1", AssetType.CONCEPT, "极不可能却影响巨大的事件"))
    notion = _RecordingNotion()

    page_id = WriterService(
        llm=FakeLLMClient(response="# 黑天鹅\n\n极不可能却影响巨大的事件"),
        notion=notion,
    ).write([_topic()], repo)

    assert page_id == "page_001"
    assert notion.stored == [("黑天鹅", "# 黑天鹅\n\n极不可能却影响巨大的事件")]


def test_write_raises_when_markdown_lacks_h1() -> None:
    with pytest.raises(ValueError, match="Missing H1 title."):
        WriterService(
            llm=FakeLLMClient(response="无标题正文"),
            notion=_RecordingNotion(),
        ).write([], AssetRepository())


def test_default_notion_requires_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARKMIND_NOTION_TOKEN", raising=False)
    monkeypatch.delenv("ARKMIND_NOTION_DATABASE_ID", raising=False)

    with pytest.raises(MissingNotionConfigError):
        WriterService()
