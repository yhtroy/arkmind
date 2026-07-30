"""Runtime environment configuration for real LLM providers.

Reads the *runtime environment* settings (API key, base URL) from environment
variables, deliberately kept separate from ``ModelConfig`` (which carries only
inference parameters: ``model`` and ``temperature``). See TASK-005 contract.

Environment variables:

* ``ARKMIND_LLM_API_KEY`` — required for real providers.
* ``ARKMIND_LLM_BASE_URL`` — optional; defaults to the OpenAI public endpoint.
  Point it at any OpenAI-compatible endpoint (DeepSeek, Ollama, vLLM, ...).
"""

from __future__ import annotations

import os

from arkmind.runtime.exceptions import MissingApiKeyError

_API_KEY_ENV = "ARKMIND_LLM_API_KEY"
_BASE_URL_ENV = "ARKMIND_LLM_BASE_URL"
_DEFAULT_BASE_URL = "https://api.openai.com/v1"


def load_api_key() -> str:
    """Return the LLM API key, or raise ``MissingApiKeyError`` if unset/empty."""
    key = os.environ.get(_API_KEY_ENV)
    if not key:
        raise MissingApiKeyError(_API_KEY_ENV)
    return key


def load_base_url() -> str:
    """Return the configured base URL, or the OpenAI public endpoint by default."""
    return os.environ.get(_BASE_URL_ENV) or _DEFAULT_BASE_URL
