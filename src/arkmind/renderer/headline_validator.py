"""Headline validation for the Renderer (M4 Renderer, Task-002).

The WeChat (公众号) Markdown target requires every article to carry a legal
level-1 heading (``# 标题``). The Renderer is a *validator*, not a formatter: it
only checks that a Writer-produced H1 exists. It never creates, rewrites or adds
a title, never injects separators or lead-ins, and never calls an LLM. A missing
H1 is a hard failure surfaced to the CLI as a non-zero exit.
"""

from __future__ import annotations

import re


class MissingH1Error(ValueError):
    """Raised when an article lacks a level-1 Markdown heading."""


class HeadlineValidator:
    """Assert that an article carries a legal level-1 Markdown heading."""

    # ATX H1: up to 3 leading spaces, exactly one '#', whitespace, then content.
    # A single '#' distinguishes H1 from '##' (H2) and deeper levels.
    _H1 = re.compile(r"^ {0,3}#[ \t]+\S")

    def validate(self, article: str) -> None:
        if not self.has_h1(article):
            raise MissingH1Error("Missing H1 title.")

    def has_h1(self, article: str) -> bool:
        return any(self._H1.match(line) for line in article.splitlines())
