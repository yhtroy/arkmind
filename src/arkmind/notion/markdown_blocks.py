"""Markdown -> Notion Blocks converter (Editorial Database v2).

The Writer keeps producing Markdown (its output contract is unchanged); this
module is the single place that turns that Markdown into the ``children``
(Page Body blocks) of a Notion page. The Writer never sees Notion.

Covered Markdown subset — everything the Writer's real output currently uses
(H1-H3 headings, paragraphs, bullet lists, quotes, dividers, code fences) plus
the common inline spans (**bold**, *italic*, `code`, [link](url)). Unsupported
syntax falls back to a plain paragraph; nothing is ever dropped.
"""

from __future__ import annotations

import re

_RICH_TEXT_LIMIT = 2000

_H1 = re.compile(r"^ {0,3}#[ \t]+(.*)$")
_H2 = re.compile(r"^ {0,3}##[ \t]+(.*)$")
_H3 = re.compile(r"^ {0,3}###[ \t]+(.*)$")
_QUOTE = re.compile(r"^ {0,3}>[ \t]?(.*)$")
_LIST = re.compile(r"^ {0,3}[-*][ \t]+(.*)$")
_DIVIDER = re.compile(r"^ {0,3}-{3,}\s*$")
_CODE_FENCE = re.compile(r"^ {0,3}`{3}")
_INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*\n]+?\*|`[^`\n]+`|\[[^\]\n]+]\([^)\n]+\))")

_TYPES = {
    "**": "bold",
    "*": "italic",
    "`": "code",
}


def markdown_to_blocks(markdown: str) -> list[dict[str, object]]:
    """Convert a Markdown document into a list of Notion block objects."""
    blocks: list[dict[str, object]] = []
    paragraph: list[str] = []
    quote_lines: list[str] = []
    list_lines: list[str] = []
    code_lines: list[str] | None = None

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(_paragraph("\n".join(paragraph).strip()))
            paragraph.clear()

    def flush_quote() -> None:
        if quote_lines:
            blocks.append(
                {
                    "object": "block",
                    "type": "quote",
                    "quote": _rich_text("\n".join(quote_lines).strip()),
                }
            )
            quote_lines.clear()

    def flush_list() -> None:
        if list_lines:
            for item in list_lines:
                blocks.append(
                    {
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": _rich_text(item),
                    }
                )
            list_lines.clear()

    def flush_all() -> None:
        flush_paragraph()
        flush_quote()
        flush_list()

    for line in markdown.splitlines():
        if code_lines is not None:
            if _CODE_FENCE.match(line):
                blocks.append(
                    {
                        "object": "block",
                        "type": "code",
                        "code": _rich_text("\n".join(code_lines)),
                    }
                )
                code_lines = None
            else:
                code_lines.append(line)
            continue
        if _CODE_FENCE.match(line):
            flush_all()
            code_lines = []
            continue
        if not line.strip():
            flush_all()
            continue

        match = _H1.match(line)
        if match:
            flush_all()
            blocks.append(_heading(1, match.group(1)))
            continue
        match = _H2.match(line)
        if match:
            flush_all()
            blocks.append(_heading(2, match.group(1)))
            continue
        match = _H3.match(line)
        if match:
            flush_all()
            blocks.append(_heading(3, match.group(1)))
            continue
        match = _QUOTE.match(line)
        if match:
            flush_paragraph()
            flush_list()
            quote_lines.append(match.group(1))
            continue
        match = _LIST.match(line)
        if match:
            flush_paragraph()
            flush_quote()
            list_lines.append(match.group(1))
            continue
        if _DIVIDER.match(line):
            flush_all()
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            continue
        flush_quote()
        flush_list()
        paragraph.append(line)

    if code_lines is not None:  # unterminated fence: keep as code block
        blocks.append(
            {"object": "block", "type": "code", "code": _rich_text("\n".join(code_lines))}
        )
    flush_all()
    return blocks


def _heading(level: int, text: str) -> dict[str, object]:
    block_type = f"heading_{level}"
    return {"object": "block", "type": block_type, block_type: _rich_text(text.strip())}


def _paragraph(text: str) -> dict[str, object]:
    return {"object": "block", "type": "paragraph", "paragraph": _rich_text(text)}


def _rich_text(text: str) -> dict[str, object]:
    """Split ``text`` into Notion rich-text spans with inline annotations."""
    spans: list[dict[str, object]] = []
    for index, piece in enumerate(_INLINE.split(text)):
        if index % 2 == 0:
            if piece:
                spans.append({"type": "text", "text": {"content": piece}})
            continue
        if piece.startswith("[") and "](" in piece:
            label, url = piece[1:].split("](", 1)
            spans.append(
                {"type": "text", "text": {"content": label, "link": {"url": url.rstrip(")")}}}
            )
            continue
        for marker, annotation in _TYPES.items():
            if piece.startswith(marker) and piece.endswith(marker):
                spans.append(
                    {
                        "type": "text",
                        "text": {"content": piece[len(marker) : -len(marker)]},
                        "annotations": {annotation: True},
                    }
                )
                break
    return {"rich_text": _chunk(spans)}


def _chunk(spans: list[dict[str, object]]) -> list[dict[str, object]]:
    """Split spans whose content exceeds the per-object rich-text limit (2000).

    A block's rich_text array may hold many objects, so a long paragraph is
    split into adjacent spans with identical annotations instead of being cut.
    """
    chunks: list[dict[str, object]] = []
    for span in spans:
        text = span["text"]
        assert isinstance(text, dict)
        content = text.get("content")
        assert isinstance(content, str)
        if len(content) <= _RICH_TEXT_LIMIT:
            chunks.append(span)
            continue
        for start in range(0, len(content), _RICH_TEXT_LIMIT):
            chunk_text: dict[str, object] = {"content": content[start : start + _RICH_TEXT_LIMIT]}
            if "link" in text:
                chunk_text["link"] = text["link"]
            chunk: dict[str, object] = {"type": "text", "text": chunk_text}
            if "annotations" in span:
                chunk["annotations"] = span["annotations"]
            chunks.append(chunk)
    return chunks
