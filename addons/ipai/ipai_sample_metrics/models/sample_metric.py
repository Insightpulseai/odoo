# -*- coding: utf-8 -*-
# Copyright 2026 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

from datetime import date

from odoo import api, fields, models


class SampleMetric(models.Model):
    """IPAI Sample Metric model for tracking analytics metrics.

    This model demonstrates a complete OCA-style Odoo 18 CE module with:
    - Standard CRUD fields
    - Computed fields with store
    - API-ready helper methods for XML-RPC/JSON-RPC integration
    """

    _name = "ipai.sample.metric"
    _description = "IPAI Sample Metric"
    _order = "date desc, name"

    name = fields.Char(
        required=True,
        help="Human readable metric label",
    )
    code = fields.Char(
        required=True,
        index=True,
        help="Technical metric code, e.g. CONV_RATE",
    )
    date = fields.Date(
        default=lambda self: date.today(),
        index=True,
    )
    brand_id = fields.Many2one(
        "res.partner",
        string="Brand",
        domain=[("is_company", "=", True)],
    )
    store_id = fields.Many2one(
        "res.partner",
        string="Store",
    )
    value = fields.Float(
        required=True,
        help="Numeric value of metric",
    )
    unit = fields.Selection(
        [
            ("percent", "%"),
            ("count", "Count"),
            ("amount", "Amount"),
        ],
        default="percent",
        required=True,
    )
    notes = fields.Text()
    active = fields.Boolean(default=True)

    # KPI flags / derived info
    is_alert = fields.Boolean(
        compute="_compute_is_alert",
        store=True,
        help="Auto flag when metric looks abnormal",
    )

    @api.depends("value", "unit")
    def _compute_is_alert(self):
        """Flag metrics that appear abnormal based on simple thresholds."""
        for rec in self:
            if rec.unit == "percent":
                rec.is_alert = rec.value < 10 or rec.value > 95
            else:
                rec.is_alert = False

    # --- API-ready helper methods ---

    @api.model
    def create_from_payload(self, payload):
        """Idempotent-ish helper for external systems.

        Expected payload: dict with keys:
            name, code, date, brand_id, store_id, value, unit, notes

        Returns:
            int: ID of the created record

        Raises:
            ValueError: If required fields are missing
        """
        required = {"name", "code", "value"}
        missing = required - set(
            k for k in payload.keys() if payload.get(k) not in (None, "")
        )
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")
        return self.create(payload).id

    @api.model
    def get_metrics(self, filters=None, limit=100):
        """Simple read API for XML-RPC/JSON-RPC.

        Args:
            filters: domain list or None (defaults to [])
            limit: max records to return (default 100)

        Returns:
            list: List of dicts with metric data
        """
        domain = filters or []
        records = self.search(domain, limit=limit)
        return [
            {
                "id": r.id,
                "name": r.name,
                "code": r.code,
                "date": r.date.isoformat() if r.date else None,
                "brand_id": r.brand_id.id if r.brand_id else None,
                "store_id": r.store_id.id if r.store_id else None,
                "value": r.value,
                "unit": r.unit,
                "is_alert": r.is_alert,
            }
            for r in records
        ]

    # --- Supabase sync helpers ---

    @api.model
    def export_to_supabase_payload(self, limit=5000, since_date=None):
        """Export metrics as payload for Supabase upsert.

        Designed to be called via XML-RPC from external sync scripts.
        Returns data in format matching ipai.ipai_sample_metrics table.

        Args:
            limit: max records to export (default 5000)
            since_date: optional ISO date string to filter recent changes

        Returns:
            list: List of dicts ready for Supabase upsert
        """
        domain = [("active", "=", True)]
        if since_date:
            domain.append(("write_date", ">=", since_date))

        records = self.search(domain, limit=limit, order="write_date desc")
        payload = []
        for r in records:
            payload.append({
                "odoo_id": r.id,
                "name": r.name,
                "code": r.code,
                "date": r.date.isoformat() if r.date else None,
                "brand_id": r.brand_id.id if r.brand_id else None,
                "store_id": r.store_id.id if r.store_id else None,
                "value": r.value,
                "unit": r.unit,
                "is_alert": r.is_alert,
                "notes": r.notes or "",
                "active": r.active,
            })
        return payload

    @api.model
    def get_sync_stats(self):
        """Get sync statistics for monitoring.

        Returns:
            dict: Count of total, active, and alert metrics
        """
        return {
            "total": self.search_count([]),
            "active": self.search_count([("active", "=", True)]),
            "alerts": self.search_count([("is_alert", "=", True)]),
        }
