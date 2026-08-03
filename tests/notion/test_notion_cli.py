"""Tests for the Notion environment-bootstrap CLI (M5.0.1).

The network is never touched: ``NotionClient.from_env`` is replaced with a
stub so the CLI is exercised end to end (status lines, failure messages,
smoke-test output) offline.
"""

from __future__ import annotations

import io
from typing import NoReturn
from urllib.error import HTTPError

import pytest

from arkmind.notion import MissingNotionConfigError, NotionEnvironmentError, notion_cli


@pytest.fixture(autouse=True)
def _cli_argv(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the CLI as ``arkmind-notion-check`` regardless of the real argv."""
    monkeypatch.setattr("sys.argv", ["arkmind-notion-check"])


class _HealthyClient:
    """Stub client with all checks passing."""

    @staticmethod
    def verify_token() -> None:
        return None

    @staticmethod
    def verify_database() -> None:
        return None

    @staticmethod
    def create_page(
        title: str, content: str, *, book: str | None = None, author: str | None = None
    ) -> str:
        return "page_001"

    @staticmethod
    def fetch_page(page_id: str) -> dict[str, object]:
        return {
            "id": page_id,
            "properties": {
                "Title": {"title": [{"plain_text": "Hello ArkMind v2"}]},
                "Book": {"rich_text": [{"plain_text": "Smoke Book"}]},
                "Author": {"rich_text": [{"plain_text": "Smoke Author"}]},
                "Status": {"select": {"name": "Draft"}},
                "Word Count": {"number": 9},
            },
        }

    @staticmethod
    def fetch_children(page_id: str) -> list[dict[str, object]]:
        return [
            {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "Smoke Test"}]}},
            {"type": "heading_2", "heading_2": {"rich_text": [{"plain_text": "Editor Notes"}]}},
            {"type": "heading_2", "heading_2": {"rich_text": [{"plain_text": "Review"}]}},
        ]


def _patch_from_env(monkeypatch: pytest.MonkeyPatch, client: object) -> None:
    monkeypatch.setattr(
        "arkmind.notion.notion_client.NotionClient.from_env", classmethod(lambda cls: client)
    )


def test_check_reports_ready(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_from_env(monkeypatch, _HealthyClient())

    notion_cli.main()

    out = capsys.readouterr().out
    assert "OK Token" in out
    assert "OK Database" in out
    assert "OK Permission" in out
    assert "OK Ready" in out


def test_check_missing_env_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise_missing() -> NoReturn:
        raise MissingNotionConfigError("ARKMIND_NOTION_TOKEN")

    monkeypatch.setattr(
        "arkmind.notion.notion_client.NotionClient.from_env",
        classmethod(lambda cls: _raise_missing()),
    )

    with pytest.raises(SystemExit) as excinfo:
        notion_cli.main()
    assert excinfo.value.code == 1


def test_check_bad_token_fails(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class _BadTokenClient(_HealthyClient):
        @staticmethod
        def verify_token() -> None:
            raise NotionEnvironmentError("Token is invalid or revoked")

    _patch_from_env(monkeypatch, _BadTokenClient())

    with pytest.raises(SystemExit) as excinfo:
        notion_cli.main()
    assert excinfo.value.code == 1
    assert "ERROR Token is invalid" in capsys.readouterr().err


def test_check_database_not_shared_fails(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class _UnsharedClient(_HealthyClient):
        @staticmethod
        def verify_database() -> None:
            raise NotionEnvironmentError("Database not found — check … and share the database")

    _patch_from_env(monkeypatch, _UnsharedClient())

    with pytest.raises(SystemExit) as excinfo:
        notion_cli.main()
    assert excinfo.value.code == 1
    assert "ERROR Database not found" in capsys.readouterr().err


def test_smoke_creates_page_and_prints_id(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_from_env(monkeypatch, _HealthyClient())
    monkeypatch.setattr("sys.argv", ["arkmind-notion-check", "--smoke"])

    notion_cli.main()

    out = capsys.readouterr().out
    assert "OK Created Notion Page" in out
    assert "OK Page ID: page_001" in out
    assert "OK Properties: Status=Draft Word Count=9" in out
    assert "OK Body: content first, then Editor Notes / Review" in out
    assert "OK Ready" in out


def test_smoke_http_error_reports_body(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class _SchemaMismatchClient(_HealthyClient):
        @staticmethod
        def create_page(
            title: str, content: str, *, book: str | None = None, author: str | None = None
        ) -> str:
            raise HTTPError(
                "url", 400, "Bad Request", {}, io.BytesIO(b'{"message":"schema mismatch"}')
            )

    _patch_from_env(monkeypatch, _SchemaMismatchClient())
    monkeypatch.setattr("sys.argv", ["arkmind-notion-check", "--smoke"])

    with pytest.raises(SystemExit) as excinfo:
        notion_cli.main()
    assert excinfo.value.code == 1
    assert "ERROR Smoke test failed: HTTP 400" in capsys.readouterr().err


def test_smoke_verification_failure_reported(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class _WrongStatusClient(_HealthyClient):
        @staticmethod
        def fetch_page(page_id: str) -> dict[str, object]:
            page = _HealthyClient.fetch_page(page_id)
            props = page["properties"]
            assert isinstance(props, dict)
            props["Status"] = {"select": {"name": "Editing"}}
            return page

    _patch_from_env(monkeypatch, _WrongStatusClient())
    monkeypatch.setattr("sys.argv", ["arkmind-notion-check", "--smoke"])

    with pytest.raises(SystemExit) as excinfo:
        notion_cli.main()
    assert excinfo.value.code == 1
    assert "ERROR Smoke verification failed: Status" in capsys.readouterr().err


def test_smoke_verification_rejects_ai_draft_heading(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class _AiDraftClient(_HealthyClient):
        @staticmethod
        def fetch_children(page_id: str) -> list[dict[str, object]]:
            return [
                {"type": "heading_1", "heading_1": {"rich_text": [{"plain_text": "AI Draft"}]}},
                {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "Smoke Test"}]}},
                {"type": "heading_2", "heading_2": {"rich_text": [{"plain_text": "Editor Notes"}]}},
                {"type": "heading_2", "heading_2": {"rich_text": [{"plain_text": "Review"}]}},
            ]

    _patch_from_env(monkeypatch, _AiDraftClient())
    monkeypatch.setattr("sys.argv", ["arkmind-notion-check", "--smoke"])

    with pytest.raises(SystemExit) as excinfo:
        notion_cli.main()
    assert excinfo.value.code == 1
    assert "ERROR Smoke verification failed: unexpected headings" in capsys.readouterr().err
