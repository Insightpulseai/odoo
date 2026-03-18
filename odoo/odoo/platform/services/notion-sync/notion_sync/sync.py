"""Main sync engine for Notion to Databricks."""

import json
import time
from datetime import datetime

import structlog

from .client import NotionClient
from .config import Config, DEFAULT_MAPPING
from .databricks_writer import DatabricksWriter
from .models import BronzeRecord, NotionPage, SyncResult, SyncSummary
from .transform import PageTransformer

logger = structlog.get_logger()


class SyncEngine:
    """Orchestrates syncing Notion databases to Databricks."""

    def __init__(self, config: Config):
        self.config = config
        self.notion = NotionClient(config.notion)
        self.databricks = DatabricksWriter(config.databricks)
        self.mapping = DEFAULT_MAPPING
        self.logger = logger.bind(service="sync-engine")

    def setup(self) -> None:
        """Initialize required tables."""
        self.logger.info("Setting up sync infrastructure")
        self.databricks.ensure_bronze_table()
        self.databricks.ensure_watermark_table(self.config.sync.watermark_table)

    def sync_database(
        self,
        database_id: str,
        database_name: str,
        mapping_config: dict,
        full_sync: bool = False,
    ) -> SyncResult:
        """Sync a single Notion database to Databricks."""
        start_time = time.time()
        self.logger.info(
            "Starting database sync",
            database_name=database_name,
            database_id=database_id,
            full_sync=full_sync,
        )

        result = SyncResult(
            database_name=database_name,
            database_id=database_id,
            pages_synced=0,
            pages_archived=0,
            duration_seconds=0,
        )

        try:
            # Get watermark for incremental sync
            watermark = None
            if not full_sync:
                watermark = self.databricks.get_watermark(
                    database_id=database_id,
                    table_name=self.config.sync.watermark_table,
                )

            # Fetch pages from Notion
            if watermark and watermark.last_edited_time:
                self.logger.info(
                    "Incremental sync",
                    since=watermark.last_edited_time.isoformat(),
                )
                pages = list(self.notion.get_pages_since(
                    database_id=database_id,
                    since=watermark.last_edited_time,
                    page_size=self.config.sync.batch_size,
                ))
            else:
                self.logger.info("Full sync")
                pages = list(self.notion.get_all_pages(
                    database_id=database_id,
                    page_size=self.config.sync.batch_size,
                ))

            if not pages:
                self.logger.info("No pages to sync")
                result.duration_seconds = time.time() - start_time
                return result

            # Write to bronze layer
            bronze_records = self._pages_to_bronze(
                pages=pages,
                database_id=database_id,
                database_name=database_name,
            )

            if not self.config.sync.dry_run:
                self.databricks.write_bronze_records(bronze_records)

            # Transform to silver layer
            column_mappings = mapping_config.get("columns", [])
            if column_mappings:
                transformer = PageTransformer(column_mappings)
                silver_records = transformer.transform_batch(pages)

                silver_table = mapping_config.get("silver_table")
                if silver_table and not self.config.sync.dry_run:
                    self.databricks.write_silver_records(
                        table_name=silver_table,
                        records=silver_records,
                        key_columns=["id"],
                    )

            # Update watermark
            last_edited = max(p.last_edited_time for p in pages)
            if not self.config.sync.dry_run:
                self.databricks.update_watermark(
                    database_id=database_id,
                    database_name=database_name,
                    last_edited_time=last_edited,
                    record_count=len(pages),
                    table_name=self.config.sync.watermark_table,
                )

            result.pages_synced = len([p for p in pages if not p.archived])
            result.pages_archived = len([p for p in pages if p.archived])

        except Exception as e:
            self.logger.error("Sync failed", error=str(e))
            result.errors.append(str(e))
            result.success = False

        result.duration_seconds = time.time() - start_time
        return result

    def _pages_to_bronze(
        self,
        pages: list[NotionPage],
        database_id: str,
        database_name: str,
    ) -> list[BronzeRecord]:
        """Convert Notion pages to bronze records."""
        records = []
        now = datetime.utcnow()

        for page in pages:
            # Serialize properties to JSON
            payload = json.dumps({
                "id": page.id,
                "created_time": page.created_time.isoformat(),
                "last_edited_time": page.last_edited_time.isoformat(),
                "archived": page.archived,
                "properties": page.properties,
                "url": page.url,
            })

            records.append(BronzeRecord(
                page_id=page.id,
                database_id=database_id,
                database_name=database_name,
                payload=payload,
                last_edited_time=page.last_edited_time,
                synced_at=now,
                is_archived=page.archived,
            ))

        return records

    def sync_all(self, full_sync: bool = False) -> SyncSummary:
        """Sync all configured Notion databases."""
        summary = SyncSummary(started_at=datetime.utcnow())

        # Setup infrastructure first
        self.setup()

        # Database configurations
        databases = [
            ("programs", self.config.notion.programs_db_id),
            ("projects", self.config.notion.projects_db_id),
            ("budget_lines", self.config.notion.budget_lines_db_id),
            ("risks", self.config.notion.risks_db_id),
        ]

        for db_name, db_id in databases:
            mapping_config = self.mapping["databases"].get(db_name, {})

            result = self.sync_database(
                database_id=db_id,
                database_name=db_name,
                mapping_config=mapping_config,
                full_sync=full_sync,
            )

            summary.add_result(result)

        summary.complete()

        self.logger.info(
            "Sync complete",
            total_pages=summary.total_pages_synced,
            total_errors=summary.total_errors,
            duration_seconds=(summary.completed_at - summary.started_at).total_seconds()
            if summary.completed_at
            else 0,
        )

        return summary
