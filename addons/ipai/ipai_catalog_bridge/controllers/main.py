# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CatalogBridgeController(http.Controller):
    """HTTP endpoints for catalog bridge operations."""

    @http.route(
        "/ipai/catalog/search",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def search_catalog(self, query=None, asset_type=None, system=None, limit=20, **kwargs):
        """Search catalog assets.

        Args:
            query: Search query
            asset_type: Filter by type
            system: Filter by system
            limit: Max results

        Returns:
            {ok: bool, assets: list}
        """
        CatalogAsset = request.env["ipai.catalog.asset"]

        try:
            assets = CatalogAsset.search_catalog(
                query=query,
                asset_type=asset_type,
                system=system,
                limit=limit,
            )
            return {"ok": True, "assets": assets}
        except Exception as e:
            _logger.error(f"Catalog search error: {e}")
            return {"ok": False, "error": str(e)}

    @http.route(
        "/ipai/catalog/tools",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def get_tools(self, tags=None, **kwargs):
        """Get tool definitions for copilot.

        Args:
            tags: Optional list of tags to filter

        Returns:
            {ok: bool, tools: list}
        """
        CatalogTool = request.env["ipai.catalog.tool"]

        try:
            tools = CatalogTool.get_tools_for_copilot(tags=tags)
            return {"ok": True, "tools": tools}
        except Exception as e:
            _logger.error(f"Get tools error: {e}")
            return {"ok": False, "error": str(e)}

    @http.route(
        "/ipai/catalog/sync/models",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def sync_models(self, model_names=None, **kwargs):
        """Sync Odoo models to catalog.

        Args:
            model_names: Optional list of model names to sync

        Returns:
            {ok: bool, synced: int, errors: list}
        """
        # Check permission
        if not request.env.user.has_group("base.group_system"):
            return {"ok": False, "error": "Admin access required"}

        CatalogSync = request.env["ipai.catalog.sync"]

        try:
            result = CatalogSync.sync_odoo_models(model_names=model_names)
            return result
        except Exception as e:
            _logger.error(f"Sync models error: {e}")
            return {"ok": False, "error": str(e)}

    @http.route(
        "/ipai/catalog/sync/actions",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def sync_actions(self, action_xmlids=None, **kwargs):
        """Sync Odoo actions to catalog.

        Args:
            action_xmlids: Optional list of action XML IDs

        Returns:
            {ok: bool, synced: int, errors: list}
        """
        # Check permission
        if not request.env.user.has_group("base.group_system"):
            return {"ok": False, "error": "Admin access required"}

        CatalogSync = request.env["ipai.catalog.sync"]

        try:
            result = CatalogSync.sync_odoo_actions(action_xmlids=action_xmlids)
            return result
        except Exception as e:
            _logger.error(f"Sync actions error: {e}")
            return {"ok": False, "error": str(e)}

    @http.route(
        "/ipai/catalog/pull",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def pull_catalog(self, asset_type=None, system=None, limit=100, **kwargs):
        """Pull assets from Supabase catalog.

        Args:
            asset_type: Filter by type
            system: Filter by system
            limit: Max assets

        Returns:
            {ok: bool, pulled: int, errors: list}
        """
        CatalogSync = request.env["ipai.catalog.sync"]

        try:
            result = CatalogSync.pull_catalog_assets(
                asset_type=asset_type,
                system=system,
                limit=limit,
            )
            return result
        except Exception as e:
            _logger.error(f"Pull catalog error: {e}")
            return {"ok": False, "error": str(e)}

    @http.route(
        "/ipai/catalog/pull/tools",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def pull_tools(self, tags=None, **kwargs):
        """Pull tool definitions from Supabase catalog.

        Args:
            tags: Optional tags to filter

        Returns:
            {ok: bool, pulled: int, errors: list}
        """
        CatalogSync = request.env["ipai.catalog.sync"]

        try:
            result = CatalogSync.pull_catalog_tools(tags=tags)
            return result
        except Exception as e:
            _logger.error(f"Pull tools error: {e}")
            return {"ok": False, "error": str(e)}

    @http.route(
        "/ipai/catalog/asset/<string:fqdn>",
        type="json",
        auth="user",
        methods=["GET"],
    )
    def get_asset(self, fqdn, **kwargs):
        """Get a single asset by FQDN.

        Args:
            fqdn: Asset FQDN

        Returns:
            {ok: bool, asset: dict}
        """
        CatalogAsset = request.env["ipai.catalog.asset"]

        try:
            asset = CatalogAsset.search([("fqdn", "=", fqdn)], limit=1)

            if not asset:
                return {"ok": False, "error": f"Asset not found: {fqdn}"}

            return {
                "ok": True,
                "asset": {
                    "id": asset.id,
                    "fqdn": asset.fqdn,
                    "asset_type": asset.asset_type,
                    "system": asset.system,
                    "title": asset.title,
                    "description": asset.description,
                    "owner": asset.owner,
                    "tags": asset.tags,
                    "uri": asset.uri,
                    "metadata": (
                        json.loads(asset.metadata_json)
                        if asset.metadata_json
                        else {}
                    ),
                },
            }
        except Exception as e:
            _logger.error(f"Get asset error: {e}")
            return {"ok": False, "error": str(e)}
