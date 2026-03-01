"""BIR Filing Deadline - Plane Sync Extension.

Uses ipai_plane_connector for all Plane API calls instead of direct requests.
"""

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BIRFilingDeadline(models.Model):
    """Extend bir.filing.deadline with Plane sync fields."""

    _inherit = ["bir.filing.deadline", "ipai.plane.connector"]

    # Plane Integration Fields
    plane_issue_id = fields.Char(
        string="Plane Issue ID",
        readonly=True,
        copy=False,
        help="Plane issue UUID for bidirectional sync",
    )
    plane_issue_url = fields.Char(
        string="Plane Issue URL",
        compute="_compute_plane_issue_url",
        store=False,
        help="Direct link to Plane issue",
    )
    plane_sync_status = fields.Selection(
        [
            ("not_synced", "Not Synced"),
            ("synced", "Synced"),
            ("pending", "Sync Pending"),
            ("error", "Sync Error"),
        ],
        string="Plane Sync Status",
        default="not_synced",
        required=True,
    )
    plane_sync_error = fields.Text(string="Sync Error Message")
    plane_last_sync = fields.Datetime(string="Last Synced", readonly=True)

    @api.depends("plane_issue_id")
    def _compute_plane_issue_url(self):
        """Compute Plane issue URL."""
        workspace_slug = self.env["ir.config_parameter"].sudo().get_param(
            "plane.workspace_slug", "default"
        )
        project_id = self.env["ir.config_parameter"].sudo().get_param(
            "plane.bir_project_id"
        )

        for record in self:
            if record.plane_issue_id and workspace_slug and project_id:
                record.plane_issue_url = (
                    f"https://app.plane.so/{workspace_slug}/projects/{project_id}/issues/{record.plane_issue_id}"
                )
            else:
                record.plane_issue_url = False

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to sync new deadlines to Plane."""
        records = super().create(vals_list)

        # Auto-sync to Plane if configured
        if self._is_plane_sync_enabled():
            for record in records:
                try:
                    record.sync_to_plane()
                except Exception as e:
                    _logger.error(f"Failed to sync new deadline {record.id} to Plane: {e}")
                    # Continue creation even if sync fails
                    record.plane_sync_status = "error"
                    record.plane_sync_error = str(e)

        return records

    def write(self, vals):
        """Override write to sync changes to Plane."""
        res = super().write(vals)

        # Auto-sync to Plane if configured and issue exists
        if self._is_plane_sync_enabled():
            # Only sync if relevant fields changed
            sync_fields = {"status", "deadline_date", "description", "priority"}
            if sync_fields & set(vals.keys()):
                for record in self:
                    if record.plane_issue_id:
                        try:
                            record.sync_to_plane()
                        except Exception as e:
                            _logger.error(f"Failed to sync deadline {record.id} updates to Plane: {e}")
                            record.plane_sync_status = "error"
                            record.plane_sync_error = str(e)

        return res

    def sync_to_plane(self):
        """
        Sync this deadline to Plane (create or update issue).

        Returns:
            bool: True if sync successful
        """
        self.ensure_one()

        if not self._is_plane_sync_enabled():
            raise UserError("Plane sync is not configured. Set system parameters.")

        # Get Supabase Edge Function URL
        supabase_url = self.env["ir.config_parameter"].sudo().get_param("supabase.url")
        if not supabase_url:
            raise UserError("Supabase URL not configured")

        edge_function_url = f"{supabase_url}/functions/v1/plane-sync?source=odoo"

        # Prepare payload
        payload = self._prepare_plane_payload()

        # Call Edge Function
        try:
            response = self._call_plane_sync_api(edge_function_url, payload)

            if response.get("success"):
                # Update local state
                self.write({
                    "plane_issue_id": response.get("plane_issue_id"),
                    "plane_sync_status": "synced",
                    "plane_sync_error": False,
                    "plane_last_sync": fields.Datetime.now(),
                })
                _logger.info(f"Successfully synced deadline {self.id} to Plane issue {response.get('plane_issue_id')}")
                return True
            else:
                error_msg = response.get("error", "Unknown error")
                self.write({
                    "plane_sync_status": "error",
                    "plane_sync_error": error_msg,
                })
                _logger.error(f"Plane sync failed for deadline {self.id}: {error_msg}")
                return False

        except Exception as e:
            error_msg = str(e)
            self.write({
                "plane_sync_status": "error",
                "plane_sync_error": error_msg,
            })
            _logger.error(f"Exception during Plane sync for deadline {self.id}: {error_msg}")
            raise

    def _prepare_plane_payload(self):
        """
        Prepare payload for Plane sync API.

        Returns:
            dict: Payload for plane-sync Edge Function
        """
        self.ensure_one()

        # Map Odoo status to Plane state
        status_map = {
            "pending": "backlog",
            "in_progress": "started",
            "filed": "completed",
            "void": "cancelled",
        }

        # Map Odoo priority to Plane priority
        priority_map = {
            "0": "low",
            "1": "medium",
            "2": "high",
            "3": "urgent",
        }

        # Generate labels
        labels = ["area:compliance"]

        # Add form type label
        if self.form_type:
            labels.append(f"form:{self.form_type.lower().replace(' ', '-')}")

        # Add status label
        if self.status:
            labels.append(f"status:{self.status}")

        # Calculate urgency
        if self.deadline_date:
            days_until = (self.deadline_date - fields.Date.today()).days
            if days_until < 0:
                labels.append("risk:deliverability")
            elif days_until <= 2:
                labels.append("risk:deliverability")

        payload = {
            "action": "update" if self.plane_issue_id else "create",
            "entity_type": "bir.filing.deadline",
            "entity_id": self.id,
            "plane_issue_id": self.plane_issue_id or None,
            "data": {
                "name": f"[{self.form_type}] {self.description or 'BIR Filing'}",
                "description": self._format_plane_description(),
                "state": status_map.get(self.status, "backlog"),
                "priority": priority_map.get(str(self.priority or "1"), "medium"),
                "labels": labels,
                "due_date": self.deadline_date.isoformat() if self.deadline_date else None,
            },
        }

        return payload

    def _format_plane_description(self):
        """Format Plane issue description with BIR details."""
        self.ensure_one()

        lines = []
        lines.append("## BIR Tax Filing Deadline")
        lines.append("")
        lines.append(f"**Form Type**: {self.form_type}")
        lines.append(f"**Filing Period**: {self.period_start} to {self.period_end}")
        lines.append(f"**Deadline**: {self.deadline_date.strftime('%Y-%m-%d (%A)')}")
        lines.append(f"**Status**: {self.status.upper()}")
        lines.append("")

        if self.description:
            lines.append("## Description")
            lines.append(self.description)
            lines.append("")

        lines.append("## Links")
        lines.append(f"- [View in Odoo ERP](odoo://bir.filing.deadline/{self.id})")
        lines.append("")
        lines.append("---")
        lines.append("*Synced from InsightPulseAI Odoo ERP via ipai_bir_plane_sync*")

        return "\n".join(lines)

    def _call_plane_sync_api(self, url, payload):
        """Call Plane sync Edge Function via connector client.

        Args:
            url: str - Edge Function URL (used for backward compat; ignored
                 when connector routes through PlaneClient directly).
            payload: dict - Request payload

        Returns:
            dict: API response
        """
        import requests as _requests

        # Use Supabase Edge Function for sync (preserves existing relay)
        service_key = self.env["ir.config_parameter"].sudo().get_param(
            "supabase.service_role_key"
        )
        if not service_key:
            raise UserError("Supabase service role key not configured")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {service_key}",
        }
        response = _requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    @api.model
    def _is_plane_sync_enabled(self):
        """Check if Plane sync is configured.

        Uses connector base check plus BIR-specific params.
        """
        if not self._plane_enabled():
            return False
        params = self.env["ir.config_parameter"].sudo()
        return bool(
            params.get_param("supabase.url")
            and params.get_param("supabase.service_role_key")
            and params.get_param("plane.bir_project_id")
        )

    def action_sync_to_plane(self):
        """Manual sync action (button)."""
        for record in self:
            record.sync_to_plane()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Plane Sync",
                "message": f"Successfully synced {len(self)} deadline(s) to Plane",
                "type": "success",
                "sticky": False,
            },
        }

    @api.model
    def sync_all_to_plane(self):
        """
        Batch sync all deadlines to Plane.

        Useful for initial setup or recovery.

        Returns:
            dict: Sync results
        """
        deadlines = self.search([])
        total = len(deadlines)
        success = 0
        errors = 0

        for deadline in deadlines:
            try:
                if deadline.sync_to_plane():
                    success += 1
                else:
                    errors += 1
            except Exception as e:
                _logger.error(f"Batch sync failed for deadline {deadline.id}: {e}")
                errors += 1

        _logger.info(f"Batch Plane sync complete: {success}/{total} successful, {errors} errors")

        return {
            "total": total,
            "success": success,
            "errors": errors,
        }

    @api.model
    def handle_plane_webhook(self, payload, headers=None):
        """Handle incoming Plane webhook (issue updated in Plane).

        Called by Supabase Edge Function after Plane webhook received.
        Uses connector for signature verification and delivery dedup.

        Args:
            payload: dict - Webhook payload from Plane
            headers: dict - HTTP headers (optional, for verification)

        Returns:
            dict: Processing result
        """
        # Verify signature if headers provided
        if headers:
            raw_body = headers.pop("_raw_body", None)
            if raw_body and not self._plane_verify_webhook(headers, raw_body):
                return {"success": False, "error": "Invalid signature"}

            # Deduplicate
            delivery_id = headers.get("X-Plane-Delivery")
            if delivery_id:
                if self._plane_is_duplicate_delivery(delivery_id):
                    return {"success": True, "deduplicated": True}
                self._plane_record_delivery(
                    delivery_id,
                    event_type=headers.get("X-Plane-Event"),
                )

        plane_issue_id = payload.get("issue_id")
        if not plane_issue_id:
            return {"success": False, "error": "Missing issue_id"}

        # Find matching deadline
        deadline = self.search([("plane_issue_id", "=", plane_issue_id)], limit=1)
        if not deadline:
            _logger.warning(f"No deadline found for Plane issue {plane_issue_id}")
            return {"success": False, "error": "No matching deadline found"}

        # Update deadline from Plane data
        updates = {}

        # Map Plane state to Odoo status
        plane_state = payload.get("state")
        state_map = {
            "backlog": "pending",
            "started": "in_progress",
            "completed": "filed",
            "cancelled": "void",
        }
        if plane_state and plane_state in state_map:
            updates["status"] = state_map[plane_state]

        # Update if changes detected
        if updates:
            deadline.write(updates)
            _logger.info(f"Updated deadline {deadline.id} from Plane webhook: {updates}")

        return {"success": True, "deadline_id": deadline.id, "updates": updates}
