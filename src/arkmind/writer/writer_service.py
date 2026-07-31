"""Writer service (M3 Writer).

Turns a set of Topics into an Article by driving the AI Runtime:

    Topic -> PromptBuilder -> LLMClient.generate(...) -> Article

The Runtime contract is ``generate(prompt, text) -> str`` where ``prompt`` is the
system message and ``text`` the user message. Accordingly the externalised writer
instruction is passed as ``prompt`` and the loss-less Topic Context as ``text``.

The service depends only on the abstract :class:`LLMClient`; it never references a
concrete provider. The default client is :class:`FakeLLMClient`, so the whole
service stays offline (no API key, network or vendor SDK) until a real provider is
injected in Task-004.
"""

from __future__ import annotations

from arkmind.asset import AssetRepository
from arkmind.runtime import FakeLLMClient, LLMClient
from arkmind.topic import Topic
from arkmind.writer.prompt_builder import PromptBuilder
from arkmind.writer.writer_model import Article


class WriterService:
    """Generate an Article from Topics via the AI Runtime."""

    def __init__(
        self,
        llm: LLMClient | None = None,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self._llm = llm if llm is not None else FakeLLMClient()
        self._prompt_builder = prompt_builder if prompt_builder is not None else PromptBuilder()

    def build_prompt(self, topics: list[Topic], assets: AssetRepository) -> str:
        return self._prompt_builder.build(topics, assets)

    def write(self, topics: list[Topic], assets: AssetRepository) -> Article:
        instruction = self._prompt_builder.instruction()
        context = self._prompt_builder.context(topics, assets)
        response = self._llm.generate(instruction, context)
        return Article(markdown=response)
