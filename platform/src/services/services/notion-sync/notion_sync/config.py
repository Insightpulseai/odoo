"""Configuration management for Notion Sync service."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NotionConfig(BaseSettings):
    """Notion API configuration."""

    token: str = Field(..., description="Notion integration token")
    programs_db_id: str = Field(..., description="Programs database ID")
    projects_db_id: str = Field(..., description="Projects database ID")
    budget_lines_db_id: str = Field(..., description="Budget Lines database ID")
    risks_db_id: str = Field(..., description="Risks database ID")
    actions_db_id: str = Field(..., description="Actions database ID")

    model_config = SettingsConfigDict(env_prefix="NOTION_")


class DatabricksConfig(BaseSettings):
    """Databricks configuration."""

    host: str = Field(..., description="Databricks workspace URL")
    token: str = Field(..., description="Databricks access token")
    catalog: str = Field(default="ppm", description="Unity Catalog name")
    schema_bronze: str = Field(default="bronze", description="Bronze schema name")
    schema_silver: str = Field(default="silver", description="Silver schema name")
    schema_gold: str = Field(default="gold", description="Gold schema name")
    warehouse_id: str = Field(..., description="SQL warehouse ID")

    model_config = SettingsConfigDict(env_prefix="DATABRICKS_")


class SyncConfig(BaseSettings):
    """Sync behavior configuration."""

    batch_size: int = Field(default=100, description="Pages per API call")
    max_retries: int = Field(default=3, description="Max retry attempts")
    retry_delay: float = Field(default=1.0, description="Base retry delay in seconds")
    watermark_table: str = Field(
        default="bronze.sync_watermarks",
        description="Table to store sync watermarks",
    )
    dry_run: bool = Field(default=False, description="Don't write to Databricks")

    model_config = SettingsConfigDict(env_prefix="SYNC_")


class Config(BaseSettings):
    """Main configuration container."""

    notion: NotionConfig = Field(default_factory=NotionConfig)
    databricks: DatabricksConfig = Field(default_factory=DatabricksConfig)
    sync: SyncConfig = Field(default_factory=SyncConfig)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            notion=NotionConfig(),
            databricks=DatabricksConfig(),
            sync=SyncConfig(),
        )


def load_mapping_config(path: Path) -> dict[str, Any]:
    """Load database mapping configuration from YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


# Default mapping configuration
DEFAULT_MAPPING = {
    "databases": {
        "programs": {
            "bronze_partition": "programs",
            "silver_table": "silver.notion_programs",
            "columns": [
                {"source": "Name", "target": "name", "type": "title"},
                {"source": "Owner", "target": "owner", "type": "person"},
                {"source": "Start Date", "target": "start_date", "type": "date"},
                {"source": "End Date", "target": "end_date", "type": "date"},
                {"source": "Status", "target": "status", "type": "select"},
                {"source": "Description", "target": "description", "type": "rich_text"},
            ],
        },
        "projects": {
            "bronze_partition": "projects",
            "silver_table": "silver.notion_projects",
            "columns": [
                {"source": "Name", "target": "name", "type": "title"},
                {"source": "Program", "target": "program_id", "type": "relation"},
                {"source": "Budget Total", "target": "budget_total", "type": "number"},
                {"source": "Currency", "target": "currency", "type": "select"},
                {"source": "Start Date", "target": "start_date", "type": "date"},
                {"source": "End Date", "target": "end_date", "type": "date"},
                {"source": "Status", "target": "status", "type": "select"},
                {"source": "Priority", "target": "priority", "type": "select"},
                {"source": "Owner", "target": "owner", "type": "person"},
            ],
        },
        "budget_lines": {
            "bronze_partition": "budget_lines",
            "silver_table": "silver.notion_budget_lines",
            "columns": [
                {"source": "Project", "target": "project_id", "type": "relation"},
                {"source": "Category", "target": "category", "type": "select"},
                {"source": "Vendor", "target": "vendor", "type": "text"},
                {"source": "Description", "target": "description", "type": "rich_text"},
                {"source": "Amount", "target": "amount", "type": "number"},
                {"source": "Committed Date", "target": "committed_date", "type": "date"},
                {"source": "Invoice Date", "target": "invoice_date", "type": "date"},
                {"source": "Paid Date", "target": "paid_date", "type": "date"},
                {"source": "Actual Amount", "target": "actual_amount", "type": "number"},
                {"source": "Notes", "target": "notes", "type": "rich_text"},
            ],
        },
        "risks": {
            "bronze_partition": "risks",
            "silver_table": "silver.notion_risks",
            "columns": [
                {"source": "Project", "target": "project_id", "type": "relation"},
                {"source": "Title", "target": "title", "type": "title"},
                {"source": "Severity", "target": "severity", "type": "select"},
                {"source": "Probability", "target": "probability", "type": "select"},
                {"source": "Status", "target": "status", "type": "select"},
                {"source": "Mitigation", "target": "mitigation", "type": "rich_text"},
                {"source": "Owner", "target": "owner", "type": "person"},
            ],
        },
    }
}
