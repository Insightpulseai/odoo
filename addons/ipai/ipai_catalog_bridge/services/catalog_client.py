# -*- coding: utf-8 -*-
"""
Catalog Client - HTTP client for catalog-sync Edge Function.

This is a plain Python class (not an Odoo model) that handles
communication with the Supabase catalog-sync Edge Function.
"""

import json
import logging
from typing import Any, Dict, List, Optional

import requests

_logger = logging.getLogger(__name__)


class CatalogClient:
    """HTTP client for the catalog-sync Edge Function."""

    def __init__(self, function_url: str, api_key: str, timeout: int = 30):
        """Initialize the catalog client.

        Args:
            function_url: URL of the catalog-sync Edge Function
            api_key: Supabase service role key
            timeout: Request timeout in seconds
        """
        self.function_url = function_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "apikey": self.api_key,
        }

    def _request(self, action: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the catalog-sync function.

        Args:
            action: The action to perform
            data: Optional data payload

        Returns:
            Response dict with 'ok' status
        """
        try:
            response = requests.post(
                self.function_url,
                headers=self._headers(),
                json={"action": action, "data": data or {}},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            _logger.error(f"Catalog request timeout: {action}")
            return {"ok": False, "error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            _logger.error(f"Catalog request error: {action} - {e}")
            return {"ok": False, "error": str(e)}
        except json.JSONDecodeError as e:
            _logger.error(f"Catalog response parse error: {action} - {e}")
            return {"ok": False, "error": "Invalid response"}

    def register_asset(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """Register or update an asset in the catalog.

        Args:
            asset: Asset data with fqdn, asset_type, system, title, etc.

        Returns:
            {ok: bool, asset_id: str, error: str}
        """
        return self._request("register_asset", asset)

    def search_assets(
        self,
        query: Optional[str] = None,
        asset_type: Optional[str] = None,
        system: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Search assets in the catalog.

        Args:
            query: Full-text search query
            asset_type: Filter by type (table, view, odoo_model, etc.)
            system: Filter by system (odoo, supabase, scout, etc.)
            tags: Filter by tags
            limit: Maximum results

        Returns:
            {ok: bool, assets: list, error: str}
        """
        data = {"limit": limit}
        if query:
            data["query"] = query
        if asset_type:
            data["asset_type"] = asset_type
        if system:
            data["system"] = system
        if tags:
            data["tags"] = tags

        return self._request("search_assets", data)

    def get_tools(self, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get tool definitions for AI copilot.

        Args:
            tags: Optional tags to filter by

        Returns:
            {ok: bool, tools: list, error: str}
        """
        data = {}
        if tags:
            data["tags"] = tags

        return self._request("get_tools", data)

    def get_tool_binding(self, tool_key: str) -> Dict[str, Any]:
        """Get the binding configuration for a tool.

        Args:
            tool_key: Tool key (e.g., odoo.create_record)

        Returns:
            {ok: bool, binding: dict, error: str}
        """
        return self._request("get_tool_binding", {"tool_key": tool_key})

    def sync_odoo_models(
        self,
        odoo_url: str,
        odoo_db: str,
        models: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Sync Odoo models to the catalog.

        Args:
            odoo_url: Odoo instance URL
            odoo_db: Database name
            models: List of model info dicts

        Returns:
            {ok: bool, synced: int, errors: list}
        """
        return self._request(
            "sync_odoo_models",
            {
                "request": {
                    "odoo_url": odoo_url,
                    "odoo_db": odoo_db,
                },
                "models": models,
            },
        )

    def sync_scout_views(
        self,
        schema_name: Optional[str] = None,
        include_views: bool = True,
    ) -> Dict[str, Any]:
        """Sync Scout views to the catalog.

        Args:
            schema_name: Schema name (default: scout_gold)
            include_views: Include views (default: True)

        Returns:
            {ok: bool, synced: int, errors: list}
        """
        data = {"include_views": include_views}
        if schema_name:
            data["schema_name"] = schema_name

        return self._request("sync_scout_views", data)

    def get_lineage(
        self,
        fqdn: str,
        direction: str = "upstream",
        depth: int = 3,
    ) -> Dict[str, Any]:
        """Get lineage graph for an asset.

        Args:
            fqdn: Asset FQDN
            direction: 'upstream' or 'downstream'
            depth: Max depth to traverse

        Returns:
            {ok: bool, lineage: list, error: str}
        """
        return self._request(
            "get_lineage",
            {
                "fqdn": fqdn,
                "direction": direction,
                "depth": depth,
            },
        )

    def check_permission(
        self,
        fqdn: str,
        principal_key: str,
        permission: str = "read",
    ) -> Dict[str, Any]:
        """Check if a principal has permission on an asset.

        Args:
            fqdn: Asset FQDN
            principal_key: Principal identifier (user, role, etc.)
            permission: Permission to check (read, write, execute)

        Returns:
            {ok: bool, allowed: bool, error: str}
        """
        return self._request(
            "check_permission",
            {
                "fqdn": fqdn,
                "principal_key": principal_key,
                "permission": permission,
            },
        )

    # -------------------------------------------------------------------------
    # Semantic Model Methods
    # -------------------------------------------------------------------------

    def _semantic_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make a request to a semantic Edge Function.

        Args:
            endpoint: Function name (semantic-import-osi, semantic-export-osi, semantic-query)
            method: HTTP method
            data: Request body
            params: Query parameters

        Returns:
            Response dict
        """
        # Build URL for different semantic functions
        base_url = self.function_url.rsplit("/", 1)[0]  # Remove catalog-sync
        url = f"{base_url}/{endpoint}"

        try:
            if method == "GET":
                response = requests.get(
                    url,
                    headers=self._headers(),
                    params=params,
                    timeout=self.timeout,
                )
            else:
                response = requests.post(
                    url,
                    headers=self._headers(),
                    json=data or {},
                    timeout=self.timeout,
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            _logger.error(f"Semantic request timeout: {endpoint}")
            return {"ok": False, "error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            _logger.error(f"Semantic request error: {endpoint} - {e}")
            return {"ok": False, "error": str(e)}
        except json.JSONDecodeError as e:
            _logger.error(f"Semantic response parse error: {endpoint} - {e}")
            return {"ok": False, "error": "Invalid response"}

    def import_semantic_model(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Import a semantic model via OSI format.

        Args:
            payload: OSI-formatted payload with model, dimensions, metrics

        Returns:
            {ok: bool, model_id: str, stats: dict, error: str}
        """
        return self._semantic_request("semantic-import-osi", data=payload)

    def export_semantic_model(
        self,
        asset_fqdn: str,
        model_name: str,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Export a semantic model.

        Args:
            asset_fqdn: Asset FQDN
            model_name: Semantic model name
            format: Output format (json, yaml, both)

        Returns:
            {ok: bool, json: dict, yaml: str, error: str}
        """
        return self._semantic_request(
            "semantic-export-osi",
            method="GET",
            params={
                "asset_fqdn": asset_fqdn,
                "model_name": model_name,
                "format": format,
            },
        )

    def query_semantic_model(
        self,
        asset_fqdn: str,
        model_name: str,
        dimensions: List[str],
        metrics: List[str],
        filters: Optional[List[Dict]] = None,
        time_grain: Optional[str] = None,
        time_range: Optional[Dict[str, str]] = None,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        """Query a semantic model and get resolved SQL plan.

        Args:
            asset_fqdn: Asset FQDN
            model_name: Semantic model name
            dimensions: List of dimension names
            metrics: List of metric names
            filters: Optional filter conditions
            time_grain: Optional time grain override
            time_range: Optional time range {start, end}
            limit: Max rows

        Returns:
            {ok: bool, plan: dict, validation: dict, error: str}
        """
        data = {
            "asset_fqdn": asset_fqdn,
            "model_name": model_name,
            "dimensions": dimensions,
            "metrics": metrics,
            "limit": limit,
        }
        if filters:
            data["filters"] = filters
        if time_grain:
            data["time_grain"] = time_grain
        if time_range:
            data["time_range"] = time_range

        return self._semantic_request("semantic-query", data=data)

    def get_semantic_models(
        self,
        asset_fqdn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get list of semantic models.

        Args:
            asset_fqdn: Optional asset FQDN to filter

        Returns:
            {ok: bool, models: list, error: str}
        """
        # Use catalog-sync to search for semantic assets
        search_query = asset_fqdn or "semantic"
        result = self.search_assets(
            query=search_query,
            asset_type="model",
            limit=100,
        )

        if not result.get("ok"):
            return result

        # For each asset, get the semantic model details
        models = []
        for asset in result.get("assets", []):
            # Extract model name from FQDN (e.g., fqdn.semantic.modelname)
            parts = asset.get("fqdn", "").split(".semantic.")
            if len(parts) == 2:
                model_name = parts[1]
                export_result = self.export_semantic_model(
                    parts[0], model_name, format="json"
                )
                if export_result.get("ok"):
                    model_data = export_result.get("json", {})
                    model_data["asset_fqdn"] = parts[0]
                    models.append(model_data)

        return {"ok": True, "models": models}
