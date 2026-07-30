"""LLM client abstraction for the AI Runtime (Runtime Contract v1).

The Runtime is deliberately neutral: a client maps ``(prompt, text) -> str`` and
nothing more. It never knows about Knowledge, Asset, Topic, Outline or Renderer.
The return value is always a plain ``str``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Map a loaded prompt plus body text to a single string response."""

    @abstractmethod
    def generate(self, prompt: str, text: str) -> str:
        """Return the model response as a plain string."""


class FakeLLMClient(LLMClient):
    """Deterministic, offline stand-in for a real LLM.

    Returns a fixed ``response`` when one is supplied, otherwise echoes the
    ``text`` it receives. Performs no I/O or network access, keeping the Runtime
    test suite fully offline.
    """

    def __init__(self, response: str | None = None) -> None:
        self._response = response

    def generate(self, prompt: str, text: str) -> str:
        return self._response if self._response is not None else text
