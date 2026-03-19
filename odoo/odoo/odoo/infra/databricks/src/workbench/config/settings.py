"""Configuration settings for the workbench."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment."""

    # Environment
    env: Literal["dev", "staging", "prod"] = Field(
        default="dev", description="Deployment environment"
    )

    # Unity Catalog
    catalog: str = Field(default="dev_ppm", description="Unity Catalog name")
    schema_bronze: str = Field(default="bronze", description="Bronze schema name")
    schema_silver: str = Field(default="silver", description="Silver schema name")
    schema_gold: str = Field(default="gold", description="Gold schema name")

    # Databricks
    databricks_host: str = Field(default="", description="Databricks workspace host")
    databricks_token: str = Field(default="", description="Databricks access token")
    warehouse_id: str = Field(default="", description="SQL warehouse ID")

    # Notion
    notion_token: str = Field(default="", description="Notion integration token")

    # Azure
    azure_subscription_id: str = Field(default="", description="Azure subscription ID")
    azure_client_id: str = Field(default="", description="Azure client ID")
    azure_client_secret: str = Field(default="", description="Azure client secret")
    azure_tenant_id: str = Field(default="", description="Azure tenant ID")

    @classmethod
    def from_env(cls) -> Settings:
        """Load settings from environment variables."""
        return cls(
            env=os.getenv("ENV", "dev"),
            catalog=os.getenv("DATABRICKS_CATALOG", "dev_ppm"),
            schema_bronze=os.getenv("SCHEMA_BRONZE", "bronze"),
            schema_silver=os.getenv("SCHEMA_SILVER", "silver"),
            schema_gold=os.getenv("SCHEMA_GOLD", "gold"),
            databricks_host=os.getenv("DATABRICKS_HOST", ""),
            databricks_token=os.getenv("DATABRICKS_TOKEN", ""),
            warehouse_id=os.getenv("WAREHOUSE_ID", ""),
            notion_token=os.getenv("NOTION_TOKEN", ""),
            azure_subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID", ""),
            azure_client_id=os.getenv("AZURE_CLIENT_ID", ""),
            azure_client_secret=os.getenv("AZURE_CLIENT_SECRET", ""),
            azure_tenant_id=os.getenv("AZURE_TENANT_ID", ""),
        )

    def get_bronze_path(self, table: str) -> str:
        """Get fully qualified bronze table path."""
        return f"{self.catalog}.{self.schema_bronze}.{table}"

    def get_silver_path(self, table: str) -> str:
        """Get fully qualified silver table path."""
        return f"{self.catalog}.{self.schema_silver}.{table}"

    def get_gold_path(self, table: str) -> str:
        """Get fully qualified gold table path."""
        return f"{self.catalog}.{self.schema_gold}.{table}"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings.from_env()
