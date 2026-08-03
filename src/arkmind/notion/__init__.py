"""Notion package (M5, Task-003).

Notion is platform infrastructure: the System of Record where the Writer stores
generated content. Future capabilities (sync, search, template, database) live
here as well.
"""

from arkmind.notion.notion_client import (
    MissingNotionConfigError,
    NotionClient,
    NotionEnvironmentError,
)

__all__ = ["MissingNotionConfigError", "NotionClient", "NotionEnvironmentError"]
