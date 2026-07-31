"""Tests for RendererService (M4 Renderer, Task-001 Skeleton).

The Renderer only converts format: input Markdown must come back loss-less, with
whitespace normalised and empty input handled. No content is rewritten.
"""

from __future__ import annotations

from arkmind.renderer import RenderedArticle, RendererService


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


def test_render_handles_empty_content() -> None:
    rendered = RendererService().render("")

    assert rendered.content == ""
