"""Tests for RendererService (M4 Renderer, Task-001 Skeleton).

The Renderer only converts format: input Markdown must come back loss-less, with
whitespace normalised and empty input handled. No content is rewritten.
"""

from __future__ import annotations

import pytest

from arkmind.renderer import RenderedArticle, RendererService
from arkmind.renderer.headline_validator import HeadlineValidator, MissingH1Error


def test_render_returns_rendered_article() -> None:
    rendered = RendererService().render("# 黑天鹅\n\n正文。")

    assert isinstance(rendered, RenderedArticle)
    assert rendered.content == "# 黑天鹅\n\n正文。"


def test_render_preserves_content_words_and_order() -> None:
    article = "# 标题\n\n第一段。\n\n第二段。\n\n## 小节\n\n第三段。"

    rendered = RendererService().render(article)

    # Every heading, paragraph and its order is preserved verbatim.
    assert rendered.content == article


def test_render_collapses_extra_blank_lines() -> None:
    rendered = RendererService().render("# 标题\n\n\n\n正文。")

    assert rendered.content == "# 标题\n\n正文。"


def test_render_trims_leading_and_trailing_blank_lines_and_spaces() -> None:
    rendered = RendererService().render("\n\n# 标题  \n\n正文。   \n\n\n")

    assert rendered.content == "# 标题\n\n正文。"


def test_render_raises_when_no_h1() -> None:
    with pytest.raises(MissingH1Error):
        RendererService().render("正文没有一级标题。")


def test_render_raises_on_empty_content() -> None:
    with pytest.raises(MissingH1Error):
        RendererService().render("")


def test_headline_validator_accepts_h1() -> None:
    assert HeadlineValidator().has_h1("# 标题\n\n正文。") is True


def test_headline_validator_rejects_missing_h1() -> None:
    # A second-level heading is not a legal H1.
    assert HeadlineValidator().has_h1("## 小节\n\n正文。") is False
