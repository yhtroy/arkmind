"""Writer service (M3 Writer).

Composes Topics into an Article. ``write`` is still the LLM-free placeholder from
Task-001 — real title/prose/structure lands in Task-004. ``build_prompt`` is the
prompt path added in Task-002: it delegates to :class:`PromptBuilder`, which
resolves each Topic's asset_id references to full content and loads the
externalised writer prompt. No LLM call happens yet.
"""

from __future__ import annotations

from arkmind.asset import AssetRepository
from arkmind.topic import Topic
from arkmind.writer.prompt_builder import PromptBuilder
from arkmind.writer.writer_model import Article

_PLACEHOLDER_TITLE = "（待 Writer 生成标题）"


class WriterService:
    """Compose Topics into an Article. No LLM yet."""

    def __init__(self, prompt_builder: PromptBuilder | None = None) -> None:
        self._prompt_builder = prompt_builder if prompt_builder is not None else PromptBuilder()

    def build_prompt(self, topics: list[Topic], assets: AssetRepository) -> str:
        return self._prompt_builder.build(topics, assets)

    def write(self, topics: list[Topic]) -> Article:
        lines = [
            "> 占位内容：Writer 骨架尚未接入 LLM（M3 Task-001）。",
            "",
            f"共 {len(topics)} 个 Topic：",
        ]
        lines.extend(f"- {topic.title}" for topic in topics)
        return Article(title=_PLACEHOLDER_TITLE, body="\n".join(lines))
