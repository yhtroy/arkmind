"""AI Runtime — neutral model access: (prompt, text) -> str (Runtime Contract v1)."""

from arkmind.runtime.exceptions import MissingApiKeyError, PromptNotFoundError
from arkmind.runtime.llm_client import FakeLLMClient, LLMClient
from arkmind.runtime.model_config import ModelConfig
from arkmind.runtime.prompt_loader import PromptLoader
from arkmind.runtime.providers import OpenAICompatibleClient

__all__ = [
    "FakeLLMClient",
    "LLMClient",
    "MissingApiKeyError",
    "ModelConfig",
    "OpenAICompatibleClient",
    "PromptLoader",
    "PromptNotFoundError",
]
