"""Tests for the WriterService runtime wiring (M3 Task-003).

Exercise the chain Topic -> PromptBuilder -> LLMClient.generate -> Article using
only offline clients. No API key, network or vendor SDK is touched: the Writer
depends solely on the abstract :class:`LLMClient`.
"""

from __future__ import annotations

from datetime import UTC, datetime

from arkmind.asset import Asset, AssetRepository, AssetType
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


def test_write_drives_runtime_and_returns_article() -> None:
    repo = _repo(_asset("c1", AssetType.CONCEPT, "极不可能却影响巨大的事件"))
    llm = _RecordingLLM("# 假标题\n\n正文")

    article = WriterService(llm=llm).write([_topic()], repo)

    # Article is exactly the model response (no reshaping / parsing).
    assert article.markdown == "# 假标题\n\n正文"


def test_write_passes_instruction_as_prompt_and_context_as_text() -> None:
    repo = _repo(_asset("c1", AssetType.CONCEPT, "极不可能却影响巨大的事件"))
    llm = _RecordingLLM("ok")

    WriterService(llm=llm).write([_topic()], repo)

    # prompt = externalised writer instruction (system); text = Topic Context (user).
    assert llm.prompt is not None and "博" in llm.prompt
    assert llm.text is not None
    assert "黑天鹅" in llm.text
    assert "极不可能却影响巨大的事件" in llm.text


def test_write_uses_fake_llm_by_default_offline() -> None:
    repo = _repo(_asset("c1", AssetType.CONCEPT, "极不可能却影响巨大的事件"))

    # Default client is FakeLLMClient, which echoes the user text (the Context).
    article = WriterService().write([_topic()], repo)

    assert "黑天鹅" in article.markdown
    assert "极不可能却影响巨大的事件" in article.markdown


def test_write_returns_fake_canned_response() -> None:
    article = WriterService(llm=FakeLLMClient(response="固定文章")).write([], AssetRepository())

    assert article.markdown == "固定文章"
