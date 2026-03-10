"""Notion API client wrapper with retry logic."""

from datetime import datetime
from typing import Any, Iterator

import structlog
from notion_client import Client
from notion_client.errors import APIResponseError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import NotionConfig
from .models import NotionPage

logger = structlog.get_logger()


class NotionClient:
    """Wrapper around Notion API client with retry logic."""

    def __init__(self, config: NotionConfig):
        self.config = config
        self.client = Client(auth=config.token)
        self.logger = logger.bind(service="notion-client")

    @retry(
        retry=retry_if_exception_type(APIResponseError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def query_database(
        self,
        database_id: str,
        filter_params: dict[str, Any] | None = None,
        sorts: list[dict[str, Any]] | None = None,
        start_cursor: str | None = None,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Query a Notion database with pagination support."""
        params: dict[str, Any] = {
            "database_id": database_id,
            "page_size": min(page_size, 100),
        }

        if filter_params:
            params["filter"] = filter_params
        if sorts:
            params["sorts"] = sorts
        if start_cursor:
            params["start_cursor"] = start_cursor

        self.logger.debug(
            "Querying database",
            database_id=database_id,
            page_size=page_size,
            has_filter=bool(filter_params),
        )

        return self.client.databases.query(**params)

    def iterate_database(
        self,
        database_id: str,
        filter_params: dict[str, Any] | None = None,
        sorts: list[dict[str, Any]] | None = None,
        page_size: int = 100,
    ) -> Iterator[NotionPage]:
        """Iterate through all pages in a database."""
        start_cursor = None
        has_more = True
        total_pages = 0

        while has_more:
            response = self.query_database(
                database_id=database_id,
                filter_params=filter_params,
                sorts=sorts,
                start_cursor=start_cursor,
                page_size=page_size,
            )

            for result in response.get("results", []):
                total_pages += 1
                yield NotionPage(
                    id=result["id"],
                    created_time=datetime.fromisoformat(
                        result["created_time"].replace("Z", "+00:00")
                    ),
                    last_edited_time=datetime.fromisoformat(
                        result["last_edited_time"].replace("Z", "+00:00")
                    ),
                    archived=result.get("archived", False),
                    properties=result.get("properties", {}),
                    url=result.get("url"),
                )

            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        self.logger.info(
            "Database iteration complete",
            database_id=database_id,
            total_pages=total_pages,
        )

    def get_pages_since(
        self,
        database_id: str,
        since: datetime,
        page_size: int = 100,
    ) -> Iterator[NotionPage]:
        """Get all pages modified since a given time."""
        filter_params = {
            "timestamp": "last_edited_time",
            "last_edited_time": {
                "after": since.isoformat(),
            },
        }

        sorts = [{"timestamp": "last_edited_time", "direction": "ascending"}]

        return self.iterate_database(
            database_id=database_id,
            filter_params=filter_params,
            sorts=sorts,
            page_size=page_size,
        )

    def get_all_pages(
        self,
        database_id: str,
        page_size: int = 100,
    ) -> Iterator[NotionPage]:
        """Get all pages in a database."""
        sorts = [{"timestamp": "last_edited_time", "direction": "ascending"}]

        return self.iterate_database(
            database_id=database_id,
            sorts=sorts,
            page_size=page_size,
        )

    @retry(
        retry=retry_if_exception_type(APIResponseError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def get_page(self, page_id: str) -> NotionPage:
        """Get a single page by ID."""
        result = self.client.pages.retrieve(page_id=page_id)

        return NotionPage(
            id=result["id"],
            created_time=datetime.fromisoformat(
                result["created_time"].replace("Z", "+00:00")
            ),
            last_edited_time=datetime.fromisoformat(
                result["last_edited_time"].replace("Z", "+00:00")
            ),
            archived=result.get("archived", False),
            properties=result.get("properties", {}),
            url=result.get("url"),
        )

    @retry(
        retry=retry_if_exception_type(APIResponseError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def get_database_info(self, database_id: str) -> dict[str, Any]:
        """Get database metadata."""
        return self.client.databases.retrieve(database_id=database_id)

    def check_health(self) -> bool:
        """Check if the Notion API is accessible."""
        try:
            # Try to retrieve the first database configured
            self.client.databases.retrieve(database_id=self.config.programs_db_id)
            return True
        except Exception as e:
            self.logger.error("Notion health check failed", error=str(e))
            return False
