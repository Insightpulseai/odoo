"""
IPAI Ops Summary Model
Read-only mirror of ops SSOT summaries from Supabase.
"""
import hashlib
import hmac
import json
import logging
import os

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiOpsSummary(models.Model):
    _name = "ipai.ops.summary"
    _description = "Ops Summary (SSOT Mirror)"
    _rec_name = "system"

    system = fields.Char(
        string="System",
        required=True,
        default="erp.insightpulseai.net",
        help="System identifier in the SSOT",
    )
    environment = fields.Char(
        string="Environment",
        required=True,
        default="prod",
        help="Environment (prod/dev/stage)",
    )
    deployment_summary_json = fields.Text(
        string="Deployment Summary (JSON)",
        help="Latest deployment information as JSON",
    )
    incident_summary_json = fields.Text(
        string="Incident Summary (JSON)",
        help="Open incidents summary as JSON",
    )
    last_synced_at = fields.Datetime(
        string="Last Synced",
        help="When the data was last refreshed from SSOT",
    )
    sync_error = fields.Text(
        string="Sync Error",
        help="Last sync error message (if any)",
    )

    # Computed fields for quick access
    deployment_version = fields.Char(
        string="Deployment Version",
        compute="_compute_deployment_fields",
        store=False,
    )
    deployment_status = fields.Char(
        string="Deployment Status",
        compute="_compute_deployment_fields",
        store=False,
    )
    open_incident_count = fields.Integer(
        string="Open Incidents",
        compute="_compute_incident_fields",
        store=False,
    )

    @api.depends("deployment_summary_json")
    def _compute_deployment_fields(self):
        for rec in self:
            if rec.deployment_summary_json:
                try:
                    data = json.loads(rec.deployment_summary_json)
                    rec.deployment_version = data.get("version", "")
                    rec.deployment_status = data.get("status", "")
                except (json.JSONDecodeError, TypeError):
                    rec.deployment_version = ""
                    rec.deployment_status = ""
            else:
                rec.deployment_version = ""
                rec.deployment_status = ""

    @api.depends("incident_summary_json")
    def _compute_incident_fields(self):
        for rec in self:
            if rec.incident_summary_json:
                try:
                    data = json.loads(rec.incident_summary_json)
                    rec.open_incident_count = int(data.get("open_count", 0))
                except (json.JSONDecodeError, TypeError, ValueError):
                    rec.open_incident_count = 0
            else:
                rec.open_incident_count = 0

    def _sign(self, body: str) -> str:
        """Generate HMAC-SHA256 signature for the request body."""
        secret = os.getenv("IPAI_OPS_SUMMARY_HMAC_SECRET", "")
        if not secret:
            raise RuntimeError("Missing IPAI_OPS_SUMMARY_HMAC_SECRET")
        return hmac.new(
            secret.encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def _fetch_summary(self, system: str, environment: str) -> dict:
        """
        Fetch summary from Supabase ops-summary Edge Function.
        Uses HMAC authentication to keep service role key out of Odoo.
        """
        url = os.getenv("IPAI_OPS_SUMMARY_URL", "")
        if not url:
            raise RuntimeError("Missing IPAI_OPS_SUMMARY_URL")

        body_obj = {"system": system, "environment": environment}
        body = json.dumps(body_obj, separators=(",", ":"), sort_keys=True)

        headers = {
            "content-type": "application/json",
            "x-ops-signature": self._sign(body),
        }

        response = requests.post(url, data=body, headers=headers, timeout=20)
        response.raise_for_status()
        return response.json()

    @api.model
    def refresh_all(self):
        """
        Refresh all ops summary records from SSOT.
        Called by cron job.
        """
        recs = self.search([])
        if not recs:
            # Create default record if none exists
            recs = self.create([{
                "system": "erp.insightpulseai.net",
                "environment": "prod"
            }])

        for rec in recs:
            try:
                data = rec._fetch_summary(rec.system, rec.environment)
                rec.write({
                    "deployment_summary_json": json.dumps(
                        data.get("deployment", {}),
                        ensure_ascii=False
                    ),
                    "incident_summary_json": json.dumps(
                        data.get("incidents", {}),
                        ensure_ascii=False
                    ),
                    "last_synced_at": fields.Datetime.now(),
                    "sync_error": False,
                })
                _logger.info(
                    "Ops summary refreshed for %s/%s",
                    rec.system,
                    rec.environment
                )
            except Exception as e:
                # Circuit breaker: keep last known good, record error
                rec.write({"sync_error": str(e)[:2000]})
                _logger.warning(
                    "Ops summary refresh failed for %s/%s: %s",
                    rec.system,
                    rec.environment,
                    e
                )

        return True
