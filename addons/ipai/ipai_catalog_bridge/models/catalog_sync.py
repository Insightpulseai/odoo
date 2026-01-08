# -*- coding: utf-8 -*-
import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CatalogSync(models.AbstractModel):
    """Service for syncing Odoo objects to Supabase catalog.

    This abstract model provides methods for:
    - Pushing Odoo models/actions to catalog
    - Pulling catalog assets to local cache
    - Registering tools for AI copilot
    """

    _name = "ipai.catalog.sync"
    _description = "Catalog Sync Service"

    @api.model
    def get_catalog_client(self):
        """Get the CatalogClient service instance."""
        from ..services.catalog_client import CatalogClient

        ICP = self.env["ir.config_parameter"].sudo()
        supabase_url = ICP.get_param("ipai_catalog.supabase_url", "")
        supabase_key = ICP.get_param("ipai_catalog.supabase_service_key", "")
        function_url = ICP.get_param(
            "ipai_catalog.function_url",
            f"{supabase_url}/functions/v1/catalog-sync" if supabase_url else "",
        )

        if not supabase_url or not supabase_key:
            _logger.warning("Catalog sync: Supabase credentials not configured")
            return None

        return CatalogClient(function_url, supabase_key)

    @api.model
    def sync_odoo_models(self, model_names=None):
        """Sync Odoo models to the catalog.

        Args:
            model_names: List of model technical names to sync.
                        If None, syncs all installed models.

        Returns:
            dict: {synced: int, errors: list}
        """
        client = self.get_catalog_client()
        if not client:
            return {"synced": 0, "errors": ["Catalog client not configured"]}

        IrModel = self.env["ir.model"]
        db_name = self.env.cr.dbname

        # Get models to sync
        domain = [("transient", "=", False)]
        if model_names:
            domain.append(("model", "in", model_names))

        models = IrModel.search(domain)
        model_infos = []

        for model in models:
            # Get field info
            try:
                model_obj = self.env[model.model]
                fields_info = []

                for field_name, field in model_obj._fields.items():
                    if field_name.startswith("_"):
                        continue

                    fields_info.append(
                        {
                            "name": field_name,
                            "type": field.type,
                            "string": field.string or field_name,
                            "required": field.required,
                            "readonly": field.readonly,
                        }
                    )

                model_infos.append(
                    {
                        "model": model.model,
                        "name": model.name,
                        "description": model.info or "",
                        "fields": fields_info[:50],  # Limit fields
                    }
                )
            except Exception as e:
                _logger.warning(f"Could not get fields for {model.model}: {e}")
                continue

        # Get Odoo URL from config
        ICP = self.env["ir.config_parameter"].sudo()
        odoo_url = ICP.get_param("web.base.url", "http://localhost:8069")

        # Call catalog-sync function
        result = client.sync_odoo_models(
            odoo_url=odoo_url,
            odoo_db=db_name,
            models=model_infos,
        )

        # Update local cache
        if result.get("ok"):
            self._update_local_cache_from_sync(model_infos, db_name)

        return result

    @api.model
    def sync_odoo_actions(self, action_xmlids=None):
        """Sync Odoo actions to the catalog.

        Args:
            action_xmlids: List of action XML IDs to sync.
                          If None, syncs common actions.

        Returns:
            dict: {synced: int, errors: list}
        """
        client = self.get_catalog_client()
        if not client:
            return {"synced": 0, "errors": ["Catalog client not configured"]}

        db_name = self.env.cr.dbname
        ICP = self.env["ir.config_parameter"].sudo()
        odoo_url = ICP.get_param("web.base.url", "http://localhost:8069")

        # Get actions to sync
        IrActWindow = self.env["ir.actions.act_window"]
        IrModelData = self.env["ir.model.data"]

        if action_xmlids:
            actions = []
            for xmlid in action_xmlids:
                try:
                    action = self.env.ref(xmlid)
                    if action._name == "ir.actions.act_window":
                        actions.append(action)
                except Exception:
                    pass
        else:
            # Get commonly used actions
            actions = IrActWindow.search(
                [("res_model", "!=", False)],
                limit=100,
                order="id",
            )

        synced = 0
        errors = []

        for action in actions:
            # Get XML ID
            xmlid = None
            data = IrModelData.search(
                [
                    ("model", "=", "ir.actions.act_window"),
                    ("res_id", "=", action.id),
                ],
                limit=1,
            )
            if data:
                xmlid = f"{data.module}.{data.name}"

            fqdn = f"odoo.{db_name}.action.{xmlid or action.id}"

            asset_data = {
                "fqdn": fqdn,
                "asset_type": "odoo_action",
                "system": "odoo",
                "title": action.name,
                "description": action.help or f"Open {action.res_model}",
                "tags": ["odoo", "action", action.res_model.split(".")[0]],
                "uri": f"{odoo_url}/web#action={action.id}",
                "metadata": {
                    "action_id": action.id,
                    "xmlid": xmlid,
                    "res_model": action.res_model,
                    "view_mode": action.view_mode,
                    "domain": action.domain,
                },
            }

            result = client.register_asset(asset_data)
            if result.get("ok"):
                synced += 1
            else:
                errors.append(f"{fqdn}: {result.get('error')}")

        return {"synced": synced, "errors": errors}

    @api.model
    def pull_catalog_assets(self, asset_type=None, system=None, limit=100):
        """Pull assets from Supabase catalog to local cache.

        Args:
            asset_type: Filter by asset type
            system: Filter by system
            limit: Max assets to pull

        Returns:
            dict: {pulled: int, errors: list}
        """
        client = self.get_catalog_client()
        if not client:
            return {"pulled": 0, "errors": ["Catalog client not configured"]}

        result = client.search_assets(
            asset_type=asset_type,
            system=system,
            limit=limit,
        )

        if not result.get("ok"):
            return {"pulled": 0, "errors": [result.get("error", "Unknown error")]}

        assets = result.get("assets", [])
        CatalogAsset = self.env["ipai.catalog.asset"]
        pulled = 0

        for asset_data in assets:
            try:
                existing = CatalogAsset.search(
                    [("fqdn", "=", asset_data["fqdn"])],
                    limit=1,
                )

                vals = {
                    "fqdn": asset_data["fqdn"],
                    "asset_type": asset_data["asset_type"],
                    "system": asset_data["system"],
                    "title": asset_data["title"],
                    "description": asset_data.get("description"),
                    "owner": asset_data.get("owner"),
                    "tags": ",".join(asset_data.get("tags", [])),
                    "uri": asset_data.get("uri"),
                    "metadata_json": json.dumps(asset_data.get("metadata", {})),
                    "supabase_id": asset_data.get("id"),
                    "last_sync": fields.Datetime.now(),
                }

                if existing:
                    existing.write(vals)
                else:
                    CatalogAsset.create(vals)

                pulled += 1
            except Exception as e:
                _logger.warning(f"Could not sync asset {asset_data.get('fqdn')}: {e}")

        return {"pulled": pulled, "errors": []}

    @api.model
    def pull_catalog_tools(self, tags=None):
        """Pull tool definitions from Supabase catalog.

        Args:
            tags: Optional list of tags to filter by

        Returns:
            dict: {pulled: int, errors: list}
        """
        client = self.get_catalog_client()
        if not client:
            return {"pulled": 0, "errors": ["Catalog client not configured"]}

        result = client.get_tools(tags=tags)

        if not result.get("ok"):
            return {"pulled": 0, "errors": [result.get("error", "Unknown error")]}

        tools = result.get("tools", [])
        CatalogTool = self.env["ipai.catalog.tool"]
        pulled = 0

        for tool_data in tools:
            try:
                existing = CatalogTool.search(
                    [("tool_key", "=", tool_data["tool_key"])],
                    limit=1,
                )

                vals = {
                    "tool_key": tool_data["tool_key"],
                    "tool_type": tool_data["tool_type"],
                    "name": tool_data["name"],
                    "description": tool_data["description"],
                    "parameters_json": json.dumps(tool_data.get("parameters", {})),
                    "returns_json": json.dumps(tool_data.get("returns", {})),
                    "requires_confirmation": tool_data.get("requires_confirmation", True),
                    "allowed_roles": ",".join(tool_data.get("allowed_roles", [])),
                    "tags": ",".join(tool_data.get("tags", [])),
                    "last_sync": fields.Datetime.now(),
                }

                if existing:
                    existing.write(vals)
                else:
                    CatalogTool.create(vals)

                pulled += 1
            except Exception as e:
                _logger.warning(f"Could not sync tool {tool_data.get('tool_key')}: {e}")

        return {"pulled": pulled, "errors": []}

    @api.model
    def sync_asset_from_catalog(self, fqdn):
        """Pull a single asset from catalog by FQDN.

        Args:
            fqdn: Asset FQDN to sync

        Returns:
            dict: {ok: bool, asset: dict, error: str}
        """
        client = self.get_catalog_client()
        if not client:
            return {"ok": False, "error": "Catalog client not configured"}

        result = client.search_assets(query=fqdn, limit=1)

        if not result.get("ok"):
            return {"ok": False, "error": result.get("error")}

        assets = result.get("assets", [])
        if not assets:
            return {"ok": False, "error": f"Asset not found: {fqdn}"}

        asset_data = assets[0]
        CatalogAsset = self.env["ipai.catalog.asset"]

        existing = CatalogAsset.search([("fqdn", "=", fqdn)], limit=1)

        vals = {
            "fqdn": asset_data["fqdn"],
            "asset_type": asset_data["asset_type"],
            "system": asset_data["system"],
            "title": asset_data["title"],
            "description": asset_data.get("description"),
            "owner": asset_data.get("owner"),
            "tags": ",".join(asset_data.get("tags", [])),
            "uri": asset_data.get("uri"),
            "metadata_json": json.dumps(asset_data.get("metadata", {})),
            "supabase_id": asset_data.get("id"),
            "last_sync": fields.Datetime.now(),
        }

        if existing:
            existing.write(vals)
            asset = existing
        else:
            asset = CatalogAsset.create(vals)

        return {
            "ok": True,
            "asset": {
                "id": asset.id,
                "fqdn": asset.fqdn,
                "title": asset.title,
            },
        }

    def _update_local_cache_from_sync(self, model_infos, db_name):
        """Update local cache after model sync."""
        CatalogAsset = self.env["ipai.catalog.asset"]

        for model_info in model_infos:
            fqdn = f"odoo.{db_name}.{model_info['model']}"

            existing = CatalogAsset.search([("fqdn", "=", fqdn)], limit=1)

            vals = {
                "fqdn": fqdn,
                "asset_type": "odoo_model",
                "system": "odoo",
                "title": model_info["name"],
                "description": model_info.get("description"),
                "tags": "odoo,model",
                "res_model": model_info["model"],
                "metadata_json": json.dumps(
                    {"fields": model_info.get("fields", [])}
                ),
                "last_sync": fields.Datetime.now(),
            }

            if existing:
                existing.write(vals)
            else:
                CatalogAsset.create(vals)
