"""Maintenance Equipment — Shelf.nu Asset Sync Extension."""

import json
import logging

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Odoo equipment state → Shelf.nu asset status mapping
EQUIPMENT_STATE_TO_SHELF = {
    "draft": "AVAILABLE",
    "normal": "AVAILABLE",
    "done": "IN_CUSTODY",
    "scrap": "AVAILABLE",  # flagged but tracked
}


class MaintenanceEquipment(models.Model):
    """Extend maintenance.equipment with Shelf.nu sync fields."""

    _inherit = "maintenance.equipment"

    shelf_asset_id = fields.Char(
        string="Shelf Asset ID",
        readonly=True,
        copy=False,
        index=True,
    )
    shelf_asset_url = fields.Char(
        string="Shelf URL",
        compute="_compute_shelf_asset_url",
        store=False,
    )
    shelf_qr_code_id = fields.Char(
        string="Shelf QR Code ID",
        readonly=True,
        copy=False,
    )
    shelf_sync_status = fields.Selection(
        [
            ("not_synced", "Not Synced"),
            ("synced", "Synced"),
            ("pending", "Sync Pending"),
            ("error", "Sync Error"),
        ],
        string="Shelf Sync",
        default="not_synced",
        required=True,
    )
    shelf_last_sync = fields.Datetime(string="Shelf Last Synced", readonly=True)
    shelf_sync_error = fields.Text(string="Shelf Sync Error")

    @api.depends("shelf_asset_id")
    def _compute_shelf_asset_url(self):
        base_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("shelf.base_url", "")
        )
        for equipment in self:
            if equipment.shelf_asset_id and base_url:
                equipment.shelf_asset_url = (
                    f"{base_url}/assets/{equipment.shelf_asset_id}"
                )
            else:
                equipment.shelf_asset_url = False

    # ------------------------------------------------------------------
    # Supabase / Shelf API helpers
    # ------------------------------------------------------------------

    @api.model
    def _shelf_supabase_call(self, method, table, payload=None, filters=None):
        """Call Shelf.nu data via Supabase REST API (PostgREST)."""
        get_param = self.env["ir.config_parameter"].sudo().get_param
        supabase_url = get_param("shelf.supabase_url", "").rstrip("/")
        service_key = get_param("shelf.supabase_service_role_key", "")

        if not all([supabase_url, service_key]):
            _logger.warning("Shelf Supabase not configured — skipping sync")
            return None

        url = f"{supabase_url}/rest/v1/{table}"
        if filters:
            url += "?" + "&".join(f"{k}=eq.{v}" for k, v in filters.items())

        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

        try:
            resp = requests.request(
                method, url, headers=headers,
                json=payload, timeout=30,
            )
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except requests.RequestException as exc:
            _logger.error("Shelf Supabase %s %s failed: %s", method, table, exc)
            return None

    @api.model
    def _is_shelf_sync_enabled(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("shelf.sync_enabled", "False")
            == "True"
        )

    # ------------------------------------------------------------------
    # Sync: Odoo → Shelf.nu (via Supabase event bus)
    # ------------------------------------------------------------------

    def sync_to_shelf(self):
        """Push this equipment record to Shelf.nu via Supabase event bus."""
        self.ensure_one()
        if not self._is_shelf_sync_enabled():
            return

        get_param = self.env["ir.config_parameter"].sudo().get_param
        org_id = get_param("shelf.organization_id", "")
        if not org_id:
            _logger.info("No Shelf organization configured — skip")
            return

        payload = {
            "source": "odoo",
            "event_type": "asset.upsert",
            "organization_id": org_id,
            "payload": json.dumps({
                "odoo_equipment_id": self.id,
                "title": self.name,
                "description": self.note or "",
                "status": EQUIPMENT_STATE_TO_SHELF.get(
                    self.equipment_assign_to or "normal", "AVAILABLE"
                ),
                "category": self.category_id.name if self.category_id else None,
                "location": self.location_id.name if self.location_id else None,
                "serial_no": self.serial_no or "",
                "assign_date": str(self.assign_date) if self.assign_date else None,
            }, default=str),
        }

        result = self._shelf_supabase_call("POST", "integration_events", payload)

        if result:
            self.write({
                "shelf_sync_status": "pending",
                "shelf_last_sync": fields.Datetime.now(),
                "shelf_sync_error": False,
            })
            self.env["shelf.sync.log"].sudo().create({
                "equipment_id": self.id,
                "direction": "odoo_to_shelf",
                "status": "success",
                "payload": json.dumps(payload, default=str),
            })
        else:
            self.write({
                "shelf_sync_status": "error",
                "shelf_sync_error": "Failed to push event to Supabase",
            })

    # ------------------------------------------------------------------
    # Sync: Shelf.nu → Odoo (webhook / polling handler)
    # ------------------------------------------------------------------

    @api.model
    def handle_shelf_webhook(self, event_data):
        """Process incoming Shelf.nu event from Supabase."""
        event_type = event_data.get("event_type", "")
        asset = event_data.get("payload", {})
        shelf_id = asset.get("id")

        if not shelf_id:
            return False

        equipment = self.search(
            [("shelf_asset_id", "=", shelf_id)], limit=1
        )

        if event_type == "asset.updated" and equipment:
            vals = {}
            if "title" in asset:
                vals["name"] = asset["title"]
            if "description" in asset:
                vals["note"] = asset["description"]
            if vals:
                vals["shelf_last_sync"] = fields.Datetime.now()
                vals["shelf_sync_status"] = "synced"
                equipment.write(vals)
            return True

        if event_type == "asset.created" and not equipment:
            self.create({
                "name": asset.get("title", "Shelf Import"),
                "note": asset.get("description", ""),
                "shelf_asset_id": shelf_id,
                "shelf_qr_code_id": asset.get("qr_code_id", ""),
                "shelf_sync_status": "synced",
                "shelf_last_sync": fields.Datetime.now(),
            })
            return True

        return False
