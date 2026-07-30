"""OpenAI-compatible LLM provider (TASK-005).

The first real implementation of :class:`LLMClient`. It targets the OpenAI
*protocol* rather than a specific vendor: by overriding the base URL it works
against OpenAI, DeepSeek, Together, vLLM or a local Ollama server — all of which
expose the same ``/chat/completions`` contract.

The class keeps the Runtime contract intact: ``generate(prompt, text) -> str``.
The ``prompt`` becomes the system message and ``text`` the user message; the
assistant reply is returned verbatim (an empty string when the model returns
no content).
"""

from __future__ import annotations

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from arkmind.runtime.config import load_api_key, load_base_url
from arkmind.runtime.llm_client import LLMClient
from arkmind.runtime.model_config import ModelConfig


class OpenAICompatibleClient(LLMClient):
    """Call any OpenAI-compatible chat endpoint through the official SDK."""

    def __init__(self, config: ModelConfig, client: OpenAI) -> None:
        self._config = config
        self._client = client

    @classmethod
    def from_env(cls, config: ModelConfig) -> OpenAICompatibleClient:
        """Build a client using ``ARKMIND_LLM_API_KEY`` / ``ARKMIND_LLM_BASE_URL``."""
        client = OpenAI(api_key=load_api_key(), base_url=load_base_url())
        return cls(config, client)

    def generate(self, prompt: str, text: str) -> str:
        system_message: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": prompt,
        }
        user_message: ChatCompletionUserMessageParam = {
            "role": "user",
            "content": text,
        }
        response = self._client.chat.completions.create(
            model=self._config.model,
            temperature=self._config.temperature,
            messages=[system_message, user_message],
        )
        return response.choices[0].message.content or ""
