"""FragmentExtractor — split page text into ordered fragments (RFC-0003).

Paragraph boundary is two or more consecutive newlines. Each surviving
paragraph is stripped of leading/trailing whitespace; empty paragraphs are
dropped. ``page_number`` is 1-based (page i+1 for ``pages[i]``); ``sequence``
is the 0-based index of the fragment within its page.
"""

from __future__ import annotations

import hashlib
import re

from arkmind.fragment.models import Fragment

_PARAGRAPH_BOUNDARY = re.compile(r"\n{2,}")


class FragmentExtractor:
    """Turn per-page text into ``Fragment`` objects in document order."""

    def extract(self, pages: list[str], source_id: str) -> list[Fragment]:
        fragments: list[Fragment] = []
        for page_index, page_text in enumerate(pages):
            page_number = page_index + 1
            sequence = 0
            for raw in _PARAGRAPH_BOUNDARY.split(page_text):
                text = raw.strip()
                if not text:
                    continue
                fragments.append(
                    Fragment(
                        fragment_id=self._fragment_id(source_id, page_number, sequence, text),
                        page_number=page_number,
                        sequence=sequence,
                        text=text,
                    )
                )
                sequence += 1
        return fragments

    @staticmethod
    def _fragment_id(source_id: str, page_number: int, sequence: int, text: str) -> str:
        payload = f"{source_id}:{page_number}:{sequence}:{text}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
