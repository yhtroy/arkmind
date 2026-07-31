"""Topic data model (RFC-M2.2-001, Topic Builder MVP).

A Topic groups Assets that share a name: Concepts and Definitions whose
name/term string is identical collapse into one Topic, and Quotes are attached
when the Topic title occurs in the quote text. Members are stored as
``asset_id`` references (not copied content) so provenance back to the Asset is
preserved and the Topic file never duplicates Asset content.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Topic(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic_id: str
    title: str
    concepts: list[str]
    definitions: list[str]
    quotes: list[str]
