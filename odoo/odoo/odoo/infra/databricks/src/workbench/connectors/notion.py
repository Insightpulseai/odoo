"""Notion API connector for data ingestion."""

from __future__ import annotations

from typing import Any

import httpx

from workbench.config.logging import get_logger
from workbench.config.settings import get_settings

logger = get_logger(__name__)


class NotionConnector:
    """Connector for Notion API operations."""

    BASE_URL = "https://api.notion.com/v1"
    API_VERSION = "2022-06-28"

    def __init__(self, token: str | None = None) -> None:
        """Initialize the Notion connector.

        Args:
            token: Notion integration token. If None, uses settings.
        """
        settings = get_settings()
        self.token = token or settings.notion_token
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": self.API_VERSION,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def query_database(
        self, database_id: str, filter_obj: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Query a Notion database with pagination.

        Args:
            database_id: Notion database ID
            filter_obj: Optional filter object

        Returns:
            List of all pages in the database
        """
        pages: list[dict[str, Any]] = []
        has_more = True
        start_cursor = None

        while has_more:
            payload: dict[str, Any] = {"page_size": 100}
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

        logger.info(f"Fetched {len(pages)} pages from database {database_id}")
        return pages

    def get_page(self, page_id: str) -> dict[str, Any]:
        """Get a single Notion page.

        Args:
            page_id: Notion page ID

        Returns:
            Page object
        """
        response = self.client.get(f"/pages/{page_id}")
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self) -> NotionConnector:
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
