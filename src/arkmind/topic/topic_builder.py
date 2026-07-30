"""TopicBuilder — aggregate Assets into Topics by deterministic rules.

RFC-M2.2-001 (Topic Builder MVP). No AI, no embeddings, no clustering
algorithm, no graph / parent / merge: Topic identity is an exact string match
on the Asset's name.

- CONCEPT: the concept name seeds / joins a Topic.
- DEFINITION: the term shares the same name space as concept names; an
  identical string joins the same Topic, otherwise it forms its own Topic.
- QUOTE: attached to every Topic whose title occurs as a substring of the
  quote text; a quote matching no Topic is dropped.

Members are stored as ``asset_id`` references. Output ordering is deterministic:
Topics are sorted by descending member count, then by title, and numbered
``topic-001`` onward. Anything beyond these rules is out of scope for the MVP
and must be raised as a TODO rather than designed here.
"""

from __future__ import annotations

from arkmind.asset import Asset, AssetType
from arkmind.topic.topic_model import Topic


def _field_after(content: str, label: str) -> str | None:
    """Return the first non-empty line following a ``label`` line, else None.

    The frozen Concept / Definition prompt output puts the name on the line
    after a ``Concept:`` / ``Term:`` label; this reads it back deterministically.
    """
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == label:
            for candidate in lines[index + 1 :]:
                if candidate.strip():
                    return candidate.strip()
            return None
    return None


class _Bucket:
    def __init__(self, title: str) -> None:
        self.title = title
        self.concepts: list[str] = []
        self.definitions: list[str] = []
        self.quotes: list[str] = []

    def size(self) -> int:
        return len(self.concepts) + len(self.definitions) + len(self.quotes)


class TopicBuilder:
    """Group Assets into Topics with exact-name deterministic rules."""

    def build(self, assets: list[Asset]) -> list[Topic]:
        buckets: dict[str, _Bucket] = {}

        def bucket(title: str) -> _Bucket:
            if title not in buckets:
                buckets[title] = _Bucket(title)
            return buckets[title]

        for asset in assets:
            if asset.content.strip() == "None":
                continue
            if asset.type is AssetType.CONCEPT:
                name = _field_after(asset.content, "Concept:")
                if name:
                    bucket(name).concepts.append(asset.asset_id)
            elif asset.type is AssetType.DEFINITION:
                term = _field_after(asset.content, "Term:")
                if term:
                    bucket(term).definitions.append(asset.asset_id)

        # Quotes attach only after every Topic title is known.
        for asset in assets:
            if asset.type is not AssetType.QUOTE:
                continue
            text = asset.content.strip()
            if text == "None":
                continue
            for title, current in buckets.items():
                if title in text:
                    current.quotes.append(asset.asset_id)

        ordered = sorted(buckets.values(), key=lambda b: (-b.size(), b.title))
        return [
            Topic(
                topic_id=f"topic-{position:03d}",
                title=current.title,
                concepts=current.concepts,
                definitions=current.definitions,
                quotes=current.quotes,
            )
            for position, current in enumerate(ordered, start=1)
        ]
