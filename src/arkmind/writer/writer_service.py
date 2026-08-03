"""Writer service (M3 Writer, M5 Task-003).

Turns a set of Topics into content and stores it in Notion, the System of
Record::

    Topic -> PromptBuilder -> LLMClient.generate(...) -> NotionClient.create_page(...) -> page id

The Runtime contract is ``generate(prompt, text) -> str`` where ``prompt`` is the
system message and ``text`` the user message. Accordingly the externalised writer
instruction is passed as ``prompt`` and the loss-less Topic Context as ``text``.

The service depends on the abstract :class:`LLMClient` and on :class:`NotionClient`;
it never references a concrete provider. Dependencies are provided by the
caller (the CLI acts as composition root) — the service never decides where its
clients come from. The default LLM client is :class:`FakeLLMClient`, so the
whole service stays offline until a real provider is injected; the Notion
client is always injected (built from ``ARKMIND_NOTION_*`` at the call site).

The LLM response is a complete Markdown document (title included) and is stored
verbatim as the page content — the Writer never reshapes it. The page title is
taken from the document's level-1 heading (``^ {0,3}#[ \\t]+``, the frozen H1
rule); a document without an H1 fails fast rather than inventing a title.
"""

from __future__ import annotations

import re

from arkmind.asset import AssetRepository
from arkmind.notion import NotionClient
from arkmind.runtime import FakeLLMClient, LLMClient
from arkmind.topic import Topic
from arkmind.writer.prompt_builder import PromptBuilder

_H1 = re.compile(r"^ {0,3}#[ \t]+(\S.*)$")


class WriterService:
    """Generate content from Topics and store it in Notion."""

    def __init__(
        self,
        notion: NotionClient,
        llm: LLMClient | None = None,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self._notion = notion
        self._llm = llm if llm is not None else FakeLLMClient()
        self._prompt_builder = prompt_builder if prompt_builder is not None else PromptBuilder()

    def build_prompt(self, topics: list[Topic], assets: AssetRepository) -> str:
        return self._prompt_builder.build(topics, assets)

    def write(
        self,
        topics: list[Topic],
        assets: AssetRepository,
        *,
        book: str | None = None,
        author: str | None = None,
    ) -> str:
        """Generate content from ``topics`` / ``assets``, store it in Notion, return the page id.

        ``book`` / ``author`` are source metadata passed through to Notion
        unchanged; the Writer never derives or reshapes them.
        """
        instruction = self._prompt_builder.instruction()
        context = self._prompt_builder.context(topics, assets)
        response = self._llm.generate(instruction, context)
        return self._notion.create_page(
            title=self._extract_title(response),
            content=response,
            book=book,
            author=author,
        )

    @staticmethod
    def _extract_title(markdown: str) -> str:
        """Return the first level-1 heading text, or raise if the document has none."""
        for line in markdown.splitlines():
            match = _H1.match(line)
            if match:
                return match.group(1).strip()
        raise ValueError("Missing H1 title.")
