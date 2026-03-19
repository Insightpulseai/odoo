"""Azure Resource Graph connector."""

from __future__ import annotations

from typing import Any

import httpx

from workbench.config.logging import get_logger
from workbench.config.settings import get_settings

logger = get_logger(__name__)


class AzureConnector:
    """Connector for Azure Resource Graph queries."""

    RESOURCE_GRAPH_URL = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources"
    API_VERSION = "2021-03-01"

    def __init__(
        self,
        subscription_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        tenant_id: str | None = None,
    ) -> None:
        """Initialize the Azure connector.

        Args:
            subscription_id: Azure subscription ID
            client_id: Azure AD client ID
            client_secret: Azure AD client secret
            tenant_id: Azure AD tenant ID
        """
        settings = get_settings()
        self.subscription_id = subscription_id or settings.azure_subscription_id
        self.client_id = client_id or settings.azure_client_id
        self.client_secret = client_secret or settings.azure_client_secret
        self.tenant_id = tenant_id or settings.azure_tenant_id
        self._token: str | None = None

    def _get_access_token(self) -> str:
        """Get Azure AD access token."""
        if self._token:
            return self._token

        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
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

    def query_resource_graph(self, query: str) -> list[dict[str, Any]]:
        """Execute an Azure Resource Graph query.

        Args:
            query: KQL query string

        Returns:
            List of query results
        """
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
        logger.info(f"Resource Graph query returned {len(results)} results")
        return results

    def get_advisor_recommendations(self) -> list[dict[str, Any]]:
        """Get Azure Advisor recommendations.

        Returns:
            List of advisor recommendations
        """
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
        return self.query_resource_graph(query)
