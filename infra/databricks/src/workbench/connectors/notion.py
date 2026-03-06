"""Notion API connector for data ingestion.

Refactored to extend BaseConnector with full SDK support:
schema declaration, incremental sync via last_edited_time,
and SyncOp emission.
"""

from __future__ import annotations

import json
from typing import Any, Iterator

import httpx

from workbench.config.logging import get_logger
from workbench.config.settings import get_settings
from workbench.connectors.base import BaseConnector
from workbench.connectors.registry import register_connector
from workbench.connectors.retry import RetryPolicy
from workbench.connectors.types import (
    ColumnDef,
    ConnectorState,
    OpType,
    SyncMode,
    SyncOp,
    TableDef,
)

logger = get_logger(__name__)


@register_connector("notion", name="Notion")
class NotionConnector(BaseConnector):
    """Connector for Notion API — databases and pages.

    Config keys:
        token: Notion integration token (falls back to settings)
        databases: dict of logical_name -> database_id
    """

    BASE_URL = "https://api.notion.com/v1"
    API_VERSION = "2022-06-28"
    retry_policy = RetryPolicy(
        max_retries=5,
        base_delay=1.0,
        retryable_exceptions=(httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException),
    )
    rate_limit = 3.0  # Notion rate limit ~3 req/s

    def __init__(self, config: dict) -> None:  # type: ignore[type-arg]
        super().__init__(config)
        settings = get_settings()
        self.token = config.get("token") or settings.notion_token
        self.databases: dict[str, str] = config.get("databases", {})
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": self.API_VERSION,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    # ------------------------------------------------------------------
    # BaseConnector interface
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:
        """Verify Notion token by listing users."""
        response = self.client.get("/users?page_size=1")
        response.raise_for_status()
        return True

    def schema(self) -> list[TableDef]:
        """Declare one table per configured Notion database."""
        columns = (
            ColumnDef("page_id", "STRING"),
            ColumnDef("database_id", "STRING"),
            ColumnDef("database_name", "STRING"),
            ColumnDef("payload", "STRING"),
            ColumnDef("last_edited_time", "TIMESTAMP"),
            ColumnDef("is_archived", "BOOLEAN"),
        )
        tables = []
        for name in self.databases:
            tables.append(
                TableDef(
                    name=f"notion_{name}",
                    columns=columns,
                    primary_key=("page_id",),
                    sync_mode=SyncMode.INCREMENTAL,
                    description=f"Raw Notion pages from {name} database",
                )
            )
        # Unified raw table
        tables.append(
            TableDef(
                name="notion_raw_pages",
                columns=columns,
                primary_key=("page_id",),
                sync_mode=SyncMode.INCREMENTAL,
                description="Unified raw Notion pages",
            )
        )
        return tables

    def update(self, state: ConnectorState) -> Iterator[SyncOp]:
        """Incrementally sync all configured Notion databases."""
        cursors: dict[str, str] = state.cursor.get("last_edited", {})

        for db_name, db_id in self.databases.items():
            since = cursors.get(db_name)
            pages = self._query_database(db_id, since=since)

            max_edited = since
            for page in pages:
                edited = page.get("last_edited_time", "")
                if not max_edited or edited > max_edited:
                    max_edited = edited

                yield SyncOp(
                    op_type=OpType.UPSERT,
                    table="notion_raw_pages",
                    data={
                        "page_id": page["id"],
                        "database_id": db_id,
                        "database_name": db_name,
                        "payload": json.dumps(page),
                        "last_edited_time": edited,
                        "is_archived": page.get("archived", False),
                    },
                )

            if max_edited:
                cursors[db_name] = max_edited

        yield SyncOp(
            op_type=OpType.CHECKPOINT,
            table="",
            cursor={"last_edited": cursors},
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    # ------------------------------------------------------------------
    # Legacy helper methods (backward-compatible)
    # ------------------------------------------------------------------

    def query_database(
        self, database_id: str, filter_obj: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Query a Notion database with pagination (legacy API)."""
        return self._query_database(database_id, filter_obj=filter_obj)

    def get_page(self, page_id: str) -> dict[str, Any]:
        """Get a single Notion page."""
        response = self.client.get(f"/pages/{page_id}")
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _query_database(
        self,
        database_id: str,
        filter_obj: dict[str, Any] | None = None,
        since: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query a Notion database with pagination and optional incremental filter."""
        pages: list[dict[str, Any]] = []
        has_more = True
        start_cursor = None

        # Build incremental filter
        if since and not filter_obj:
            filter_obj = {
                "timestamp": "last_edited_time",
                "last_edited_time": {"after": since},
            }

        while has_more:
            payload: dict[str, Any] = {
                "page_size": 100,
                "sorts": [{"timestamp": "last_edited_time", "direction": "ascending"}],
            }
            if filter_obj:
                payload["filter"] = filter_obj
            if start_cursor:
                payload["start_cursor"] = start_cursor

            response = self.client.post(f"/databases/{database_id}/query", json=payload)
            response.raise_for_status()
            data = response.json()

            pages.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")

        logger.info("Fetched %d pages from database %s", len(pages), database_id)
        return pages
