"""Project Task — Plane Work Item Sync Extension."""

import json
import logging

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Odoo stage → Plane state group mapping
STAGE_TO_PLANE_STATE = {
    "draft": "backlog",
    "open": "started",
    "pending": "started",
    "done": "completed",
    "cancelled": "cancelled",
}

# Odoo priority → Plane priority mapping
PRIORITY_TO_PLANE = {
    "0": "none",
    "1": "medium",
    "2": "high",
    "3": "urgent",
}


class ProjectTask(models.Model):
    """Extend project.task with Plane work item sync fields."""

    _inherit = "project.task"

    plane_work_item_id = fields.Char(
        string="Plane Work Item ID",
        readonly=True,
        copy=False,
        index=True,
    )
    plane_work_item_url = fields.Char(
        string="Plane URL",
        compute="_compute_plane_work_item_url",
        store=False,
    )
    plane_sync_status = fields.Selection(
        [
            ("not_synced", "Not Synced"),
            ("synced", "Synced"),
            ("pending", "Sync Pending"),
            ("error", "Sync Error"),
        ],
        string="Plane Sync",
        default="not_synced",
        required=True,
    )
    plane_last_sync = fields.Datetime(string="Plane Last Synced", readonly=True)
    plane_sync_error = fields.Text(string="Plane Sync Error")

    @api.depends("plane_work_item_id")
    def _compute_plane_work_item_url(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        base_url = get_param("plane.base_url", "")
        workspace = get_param("plane.workspace_slug", "")

        for task in self:
            if task.plane_work_item_id and base_url and workspace:
                project_id = get_param(
                    f"plane.project_map.{task.project_id.id}", ""
                )
                if project_id:
                    task.plane_work_item_url = (
                        f"{base_url}/{workspace}/projects/"
                        f"{project_id}/issues/{task.plane_work_item_id}"
                    )
                else:
                    task.plane_work_item_url = False
            else:
                task.plane_work_item_url = False

    # ------------------------------------------------------------------
    # Plane API helpers
    # ------------------------------------------------------------------

    @api.model
    def _plane_api_call(self, method, endpoint, payload=None):
        """Make authenticated call to Plane API."""
        get_param = self.env["ir.config_parameter"].sudo().get_param
        base_url = get_param("plane.api_url", "").rstrip("/")
        api_key = get_param("plane.api_key", "")
        workspace = get_param("plane.workspace_slug", "")

        if not all([base_url, api_key, workspace]):
            _logger.warning("Plane API not configured — skipping sync")
            return None

        url = f"{base_url}/api/v1/workspaces/{workspace}/{endpoint}"
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }

        try:
            resp = requests.request(
                method, url, headers=headers,
                json=payload, timeout=30,
            )
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except requests.RequestException as exc:
            _logger.error("Plane API %s %s failed: %s", method, endpoint, exc)
            return None

    @api.model
    def _is_plane_sync_enabled(self):
        return bool(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("plane.sync_enabled", "False")
            == "True"
        )

    # ------------------------------------------------------------------
    # Sync: Odoo → Plane
    # ------------------------------------------------------------------

    def sync_to_plane(self):
        """Push this task to Plane as a work item."""
        self.ensure_one()
        if not self._is_plane_sync_enabled():
            return

        get_param = self.env["ir.config_parameter"].sudo().get_param
        project_id = get_param(
            f"plane.project_map.{self.project_id.id}", ""
        )
        if not project_id:
            _logger.info(
                "No Plane project mapped for Odoo project %s — skip",
                self.project_id.id,
            )
            return

        payload = {
            "name": self.name,
            "description_html": self.description or "",
            "priority": PRIORITY_TO_PLANE.get(self.priority or "0", "none"),
        }
        if self.date_deadline:
            payload["target_date"] = str(self.date_deadline)

        if self.plane_work_item_id:
            # Update existing
            result = self._plane_api_call(
                "PATCH",
                f"projects/{project_id}/work-items/{self.plane_work_item_id}/",
                payload,
            )
        else:
            # Create new
            result = self._plane_api_call(
                "POST",
                f"projects/{project_id}/work-items/",
                payload,
            )

        if result and result.get("id"):
            self.write({
                "plane_work_item_id": result["id"],
                "plane_sync_status": "synced",
                "plane_last_sync": fields.Datetime.now(),
                "plane_sync_error": False,
            })
            self.env["plane.sync.log"].sudo().create({
                "task_id": self.id,
                "direction": "odoo_to_plane",
                "status": "success",
                "payload": json.dumps(payload, default=str),
            })
        elif result is not None:
            self.write({
                "plane_sync_status": "error",
                "plane_sync_error": json.dumps(result, default=str),
            })

    # ------------------------------------------------------------------
    # Sync: Plane → Odoo (webhook handler)
    # ------------------------------------------------------------------

    @api.model
    def handle_plane_webhook(self, event_data):
        """Process incoming Plane webhook event."""
        event_type = event_data.get("event")
        work_item = event_data.get("data", {})
        plane_id = work_item.get("id")

        if not plane_id:
            return False

        task = self.search([("plane_work_item_id", "=", plane_id)], limit=1)

        if event_type == "work_item.updated" and task:
            vals = {}
            if "name" in work_item:
                vals["name"] = work_item["name"]
            if "target_date" in work_item and work_item["target_date"]:
                vals["date_deadline"] = work_item["target_date"]
            if vals:
                vals["plane_last_sync"] = fields.Datetime.now()
                vals["plane_sync_status"] = "synced"
                task.write(vals)

            self.env["plane.sync.log"].sudo().create({
                "task_id": task.id,
                "direction": "plane_to_odoo",
                "status": "success",
                "payload": json.dumps(work_item, default=str),
            })
            return True

        if event_type == "work_item.deleted" and task:
            task.write({
                "plane_sync_status": "not_synced",
                "plane_work_item_id": False,
            })
            return True

        return False
