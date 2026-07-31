"""Writer Prompt Builder (M3 Task-002).

Builds the single Prompt string later handed to ``LLMClient.generate``. The
instruction body is externalised in ``prompts/writer.md`` (never hard-coded);
this module loads it, resolves each Topic's asset_id references to full content
via :class:`AssetResolver`, and appends a faithful Context. The Context keeps the
original Concept / Definition / Quote text intact — no summarising, rewriting or
deletion. No LLM call happens here.
"""

from __future__ import annotations

from arkmind.asset import AssetRepository
from arkmind.runtime import PromptLoader
from arkmind.topic import Topic
from arkmind.writer.asset_resolver import AssetResolver, ResolvedTopic

_EMPTY = "（无）"


class PromptBuilder:
    """Load the writer prompt and append a loss-less Topic Context."""

    def __init__(
        self, loader: PromptLoader | None = None, resolver: AssetResolver | None = None
    ) -> None:
        self._loader = loader if loader is not None else PromptLoader()
        self._resolver = resolver if resolver is not None else AssetResolver()

    def build(self, topics: list[Topic], assets: AssetRepository) -> str:
        instruction = self._loader.load("writer")
        blocks = [self._render(self._resolver.resolve(topic, assets)) for topic in topics]
        context = "\n\n".join(blocks)
        return f"{instruction}\n\n# 知识主题（Context）\n\n{context}"

    def _render(self, topic: ResolvedTopic) -> str:
        lines = [f"## {topic.title}", ""]
        for label, items in (
            ("Concepts", topic.concepts),
            ("Definitions", topic.definitions),
            ("Quotes", topic.quotes),
        ):
            lines.append(f"### {label}")
            lines.extend(items if items else [_EMPTY])
            lines.append("")
        return "\n".join(lines).rstrip()
