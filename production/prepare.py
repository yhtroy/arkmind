"""production/prepare.py — M5.5 production-input converter (small utility).

Turns one book's raw-material directory into the Writer's JSON inputs::

    production/<book>/
        notes.md      # human notes: concepts / definitions / quotes
        topic.json    # generated (arkmind-topic contract)
        asset.json    # generated (arkmind-asset contract)

``notes.md`` is the only convention this tool requires — three sections with
dash items, nothing else::

    ## 概念
    - 黑天鹅：不可预测、概率极低、一旦发生影响巨大且事后常被过度解释的事件

    ## 定义
    - 黑天鹅：指同时具备稀有性、极大冲击性和事后看似可预测性的事件

    ## 引语
    - 你不知道的事比你知道的事更有意义。

The converter never interprets item content: each dash item becomes one Asset
(CONCEPT / DEFINITION / QUOTE), and Topics group Assets by identical name
(asset_id references, same semantics as arkmind-topic). ``asset_id`` is a fresh
UUID, ``knowledge_id`` is the sha256 of the item text (no Knowledge layer in
M5.5), ``book_id`` is the directory name, ``created_at`` is generation time in
UTC. Quotes are attached to a Topic when the topic title occurs in the quote
text; unmatched quotes are left ungrouped.

Run::

    uv run python production/prepare.py production/black_swan
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

_SECTION_PATTERN = re.compile(r"^##\s+(\S+)")
_ITEM_PATTERN = re.compile(r"^-\s+(.+)$")
_NAME_SPLIT = re.compile(r"^(.+?)[：:]\s*(.*)$")


def _parse_notes(path: Path) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        section = _SECTION_PATTERN.match(line)
        if section:
            current = section.group(1)
            sections.setdefault(current, [])
            continue
        item = _ITEM_PATTERN.match(line)
        if item and current is not None:
            sections[current].append(item.group(1).strip())
    return sections


def _split_name(text: str) -> tuple[str, str]:
    match = _NAME_SPLIT.match(text)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return text, ""


def _build(book_dir: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    notes = _parse_notes(book_dir / "notes.md")
    now = datetime.now(timezone.utc)

    assets: list[dict[str, object]] = []
    topics: list[dict[str, object]] = []
    name_to_topic: dict[str, dict[str, object]] = {}

    def add_asset(type_: str, name: str, content: str) -> dict[str, object]:
        asset = {
            "asset_id": str(uuid.uuid4()),
            "book_id": book_dir.name,
            "knowledge_id": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "type": type_,
            "content": content,
            "created_at": now.isoformat(),
        }
        assets.append(asset)
        return asset

    def topic_for(name: str) -> dict[str, object]:
        topic = name_to_topic.get(name)
        if topic is None:
            topic = {
                "topic_id": f"topic-{len(topics) + 1:03d}",
                "title": name,
                "concepts": [],
                "definitions": [],
                "quotes": [],
            }
            topics.append(topic)
            name_to_topic[name] = topic
        return topic

    for item in notes.get("概念", []):
        name, content = _split_name(item)
        asset = add_asset("CONCEPT", name, content or name)
        topic_for(name)["concepts"].append(asset["asset_id"])

    for item in notes.get("定义", []):
        name, content = _split_name(item)
        asset = add_asset("DEFINITION", name, content or name)
        topic_for(name)["definitions"].append(asset["asset_id"])

    for item in notes.get("引语", []):
        asset = add_asset("QUOTE", "", item)
        for name, topic in name_to_topic.items():
            if name and name in item:
                topic["quotes"].append(asset["asset_id"])
                break

    return topics, assets


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-prepare")
    parser.add_argument("book_dir", type=Path)
    args = parser.parse_args()

    topics, assets = _build(args.book_dir)
    (args.book_dir / "topic.json").write_text(
        json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.book_dir / "asset.json").write_text(
        json.dumps(assets, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"topics: {len(topics)}, assets: {len(assets)} -> {args.book_dir}")


if __name__ == "__main__":
    main()
