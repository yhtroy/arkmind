"""Writer service (M3 Writer, Task-001 skeleton).

Turns a list of Topics into an :class:`Article`. This skeleton is deliberately
LLM-free: it produces a deterministic placeholder so the Source -> Asset ->
Topic -> Writer chain closes end to end. The real title/prose/structure will be
produced by the LLM in later M3 tasks (Prompt Builder, LLM Adapter, Article
Generator); ``write`` is the seam where that logic will land.
"""

from __future__ import annotations

from arkmind.topic import Topic
from arkmind.writer.writer_model import Article

_PLACEHOLDER_TITLE = "（待 Writer 生成标题）"


class WriterService:
    """Compose Topics into an Article. No LLM in the skeleton."""

    def write(self, topics: list[Topic]) -> Article:
        lines = [
            "> 占位内容：Writer 骨架尚未接入 LLM（M3 Task-001）。",
            "",
            f"共 {len(topics)} 个 Topic：",
        ]
        lines.extend(f"- {topic.title}" for topic in topics)
        return Article(title=_PLACEHOLDER_TITLE, body="\n".join(lines))
