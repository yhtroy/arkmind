"""Tests for the Markdown -> Notion Blocks converter (Editorial Database v2).

Pure function tests: no network, no client. They pin the conversion subset the
Writer's real output relies on — headings, paragraphs, lists, quotes, dividers,
code fences and inline annotations — plus the 2000-character rich-text chunking
that long AI paragraphs need.
"""

from __future__ import annotations

from arkmind.notion.block_builder import build_blocks


def _text(block: dict[str, object]) -> str:
    key = block["type"]
    assert isinstance(key, str)
    payload = block[key]
    assert isinstance(payload, dict)
    return "".join(
        span["text"]["content"] for span in payload["rich_text"] if span["type"] == "text"
    )


def test_empty_document_yields_no_blocks() -> None:
    assert build_blocks("") == []


def test_headings_map_to_heading_blocks() -> None:
    blocks = build_blocks("# 标题\n\n## 小节\n\n### 子节")

    assert [block["type"] for block in blocks] == ["heading_1", "heading_2", "heading_3"]
    assert [_text(block) for block in blocks] == ["标题", "小节", "子节"]


def test_paragraphs_join_adjacent_lines() -> None:
    blocks = build_blocks("第一行\n第二行\n\n第三段")

    assert [block["type"] for block in blocks] == ["paragraph", "paragraph"]
    assert [_text(block) for block in blocks] == ["第一行\n第二行", "第三段"]


def test_bullet_list_groups_consecutive_items() -> None:
    blocks = build_blocks("- 甲\n- 乙\n\n正文")

    assert [block["type"] for block in blocks] == [
        "bulleted_list_item",
        "bulleted_list_item",
        "paragraph",
    ]
    assert [_text(block) for block in blocks] == ["甲", "乙", "正文"]


def test_quote_groups_consecutive_lines() -> None:
    blocks = build_blocks("> 第一句\n> 第二句")

    assert [block["type"] for block in blocks] == ["quote"]
    assert _text(blocks[0]) == "第一句\n第二句"


def test_divider_maps_to_divider_block() -> None:
    blocks = build_blocks("正文\n\n---\n\n后文")

    assert [block["type"] for block in blocks] == ["paragraph", "divider", "paragraph"]


def test_code_fence_maps_to_code_block() -> None:
    blocks = build_blocks("```\nprint(1)\n```")

    assert [block["type"] for block in blocks] == ["code"]
    assert _text(blocks[0]) == "print(1)"


def test_unterminated_code_fence_kept_as_code() -> None:
    blocks = build_blocks("```\nprint(1)")

    assert [block["type"] for block in blocks] == ["code"]
    assert _text(blocks[0]) == "print(1)"


def test_inline_bold_italic_code_and_link() -> None:
    (block,) = build_blocks("**粗** 和 *斜* 和 `码` 和 [链](https://x.example)")

    spans = block["paragraph"]["rich_text"]
    assert [span["text"]["content"] for span in spans] == [
        "粗",
        " 和 ",
        "斜",
        " 和 ",
        "码",
        " 和 ",
        "链",
    ]
    assert spans[0]["annotations"] == {"bold": True}
    assert spans[2]["annotations"] == {"italic": True}
    assert spans[4]["annotations"] == {"code": True}
    assert spans[6]["text"]["link"] == {"url": "https://x.example"}


def test_long_paragraph_chunked_over_2000_characters() -> None:
    long = "字" * 4500  # 2000 + 2000 + 500

    (block,) = build_blocks(long)

    spans = block["paragraph"]["rich_text"]
    lengths = [len(span["text"]["content"]) for span in spans]
    assert lengths == [2000, 2000, 500]
    assert "".join(span["text"]["content"] for span in spans) == long


def test_long_bold_span_keeps_annotation_after_chunking() -> None:
    (block,) = build_blocks("**" + "字" * 4500 + "**")

    spans = block["paragraph"]["rich_text"]
    assert all(span["annotations"] == {"bold": True} for span in spans)
    assert "".join(span["text"]["content"] for span in spans) == "字" * 4500


def test_unsupported_syntax_falls_back_to_paragraph() -> None:
    (block,) = build_blocks("| 表格 | 不解析 |")

    assert block["type"] == "paragraph"
    assert _text(block) == "| 表格 | 不解析 |"
