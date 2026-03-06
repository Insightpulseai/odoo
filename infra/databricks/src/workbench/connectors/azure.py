"""Azure Resource Graph connector.

Refactored to extend BaseConnector with full SDK support.
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


@register_connector("azure", name="Azure Resource Graph")
class AzureConnector(BaseConnector):
    """Connector for Azure Resource Graph queries.

    Config keys:
        subscription_id, client_id, client_secret, tenant_id
        (all fall back to settings)
    """

    RESOURCE_GRAPH_URL = (
        "https://management.azure.com/providers/Microsoft.ResourceGraph/resources"
    )
    API_VERSION = "2021-03-01"
    retry_policy = RetryPolicy(
        max_retries=3,
        base_delay=2.0,
        retryable_exceptions=(httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException),
    )
    rate_limit = 5.0

    def __init__(self, config: dict) -> None:  # type: ignore[type-arg]
        super().__init__(config)
        settings = get_settings()
        self.subscription_id = config.get("subscription_id") or settings.azure_subscription_id
        self.client_id = config.get("client_id") or settings.azure_client_id
        self.client_secret = config.get("client_secret") or settings.azure_client_secret
        self.tenant_id = config.get("tenant_id") or settings.azure_tenant_id
        self._token: str | None = None

    # ------------------------------------------------------------------
    # BaseConnector interface
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:
        """Verify Azure credentials by acquiring a token."""
        self._get_access_token()
        return True

    def schema(self) -> list[TableDef]:
        """Declare Azure tables."""
        advisor_cols = (
            ColumnDef("recommendation_id", "STRING"),
            ColumnDef("subscription_id", "STRING"),
            ColumnDef("resource_group", "STRING"),
            ColumnDef("category", "STRING"),
            ColumnDef("impact", "STRING"),
            ColumnDef("impacted_field", "STRING"),
            ColumnDef("impacted_value", "STRING"),
            ColumnDef("short_description", "STRING"),
            ColumnDef("raw_payload", "STRING"),
            ColumnDef("last_updated", "STRING"),
        )
        resource_cols = (
            ColumnDef("resource_id", "STRING"),
            ColumnDef("name", "STRING"),
            ColumnDef("type", "STRING"),
            ColumnDef("location", "STRING"),
            ColumnDef("resource_group", "STRING"),
            ColumnDef("subscription_id", "STRING"),
            ColumnDef("raw_payload", "STRING"),
        )
        return [
            TableDef(
                name="azure_advisor_raw",
                columns=advisor_cols,
                primary_key=("recommendation_id",),
                sync_mode=SyncMode.FULL_REFRESH,
                description="Azure Advisor recommendations",
            ),
            TableDef(
                name="azure_resources_raw",
                columns=resource_cols,
                primary_key=("resource_id",),
                sync_mode=SyncMode.FULL_REFRESH,
                description="Azure resource inventory",
            ),
        ]

    def update(self, state: ConnectorState) -> Iterator[SyncOp]:
        """Full-refresh Azure Advisor recommendations and resources."""
        # Advisor recommendations
        advisor_query = """
        advisorresources
        | where type == 'microsoft.advisor/recommendations'
        | extend category = properties.category
        | extend impact = properties.impact
        | extend impactedField = properties.impactedField
        | extend impactedValue = properties.impactedValue
        | extend shortDescription = properties.shortDescription.problem
        | extend lastUpdated = properties.lastUpdated
        | project id, name, category, impact, impactedField, impactedValue,
                  shortDescription, lastUpdated, subscriptionId, resourceGroup
        """
        for rec in self._query_resource_graph(advisor_query):
            yield SyncOp(
                op_type=OpType.UPSERT,
                table="azure_advisor_raw",
                data={
                    "recommendation_id": rec.get("id"),
                    "subscription_id": rec.get("subscriptionId"),
                    "resource_group": rec.get("resourceGroup"),
                    "category": rec.get("category"),
                    "impact": rec.get("impact"),
                    "impacted_field": rec.get("impactedField"),
                    "impacted_value": rec.get("impactedValue"),
                    "short_description": rec.get("shortDescription"),
                    "raw_payload": json.dumps(rec),
                    "last_updated": rec.get("lastUpdated"),
                },
            )

        # Resource inventory
        resource_query = """
        resources
        | where type =~ 'microsoft.compute/virtualmachines'
            or type =~ 'microsoft.storage/storageaccounts'
            or type =~ 'microsoft.sql/servers/databases'
            or type =~ 'microsoft.databricks/workspaces'
        | project id, name, type, location, resourceGroup, subscriptionId
        | limit 1000
        """
        for res in self._query_resource_graph(resource_query):
            yield SyncOp(
                op_type=OpType.UPSERT,
                table="azure_resources_raw",
                data={
                    "resource_id": res.get("id"),
                    "name": res.get("name"),
                    "type": res.get("type"),
                    "location": res.get("location"),
                    "resource_group": res.get("resourceGroup"),
                    "subscription_id": res.get("subscriptionId"),
                    "raw_payload": json.dumps(res),
                },
            )

        yield SyncOp(op_type=OpType.CHECKPOINT, table="", cursor={})

    # ------------------------------------------------------------------
    # Legacy helper methods (backward-compatible)
    # ------------------------------------------------------------------

    def query_resource_graph(self, query: str) -> list[dict[str, Any]]:
        """Execute an Azure Resource Graph query (legacy API)."""
        return self._query_resource_graph(query)

    def get_advisor_recommendations(self) -> list[dict[str, Any]]:
        """Get Azure Advisor recommendations (legacy API)."""
        query = """
        advisorresources
        | where type == 'microsoft.advisor/recommendations'
        | extend category = properties.category
        | extend impact = properties.impact
        | extend impactedField = properties.impactedField
        | extend impactedValue = properties.impactedValue
        | extend shortDescription = properties.shortDescription.problem
        | extend recommendationTypeId = properties.recommendationTypeId
        | project id, name, category, impact, impactedField, impactedValue,
                  shortDescription, recommendationTypeId, subscriptionId, resourceGroup
        """
        return self._query_resource_graph(query)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_access_token(self) -> str:
        if self._token:
            return self._token
        token_url = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )
        response = httpx.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "https://management.azure.com/.default",
            },
        )
        response.raise_for_status()
        self._token = response.json()["access_token"]
        return self._token

    def _query_resource_graph(self, query: str) -> list[dict[str, Any]]:
        token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "subscriptions": [self.subscription_id],
            "query": query,
        }
        response = httpx.post(
            f"{self.RESOURCE_GRAPH_URL}?api-version={self.API_VERSION}",
            json=payload,
            headers=headers,
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("data", [])
        logger.info("Resource Graph query returned %d results", len(results))
        return results
