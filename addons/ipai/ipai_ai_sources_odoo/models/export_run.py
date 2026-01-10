# -*- coding: utf-8 -*-
"""
IPAI AI Sources - Export Run Model
===================================

Tracks export runs for monitoring and debugging.
"""
from odoo import fields, models


class IpaiKbExportRun(models.Model):
    """Record of a KB export run."""

    _name = "ipai.kb.export.run"
    _description = "IPAI KB Export Run"
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    state = fields.Selection(
        [
            ("running", "Running"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        default="running",
        required=True,
        index=True,
    )

    chunks_count = fields.Integer(
        help="Number of chunks exported in this run",
    )

    started_at = fields.Datetime(
        default=fields.Datetime.now,
        readonly=True,
    )
    completed_at = fields.Datetime(
        readonly=True,
    )
    duration_seconds = fields.Float(
        compute="_compute_duration",
        store=True,
    )

    error_message = fields.Text(
        help="Error message if export failed",
    )

    def name_get(self):
        result = []
        for rec in self:
            name = f"Export Run {rec.id} ({rec.state})"
            result.append((rec.id, name))
        return result

    def _compute_duration(self):
        for rec in self:
            if rec.started_at and rec.completed_at:
                delta = rec.completed_at - rec.started_at
                rec.duration_seconds = delta.total_seconds()
            else:
                rec.duration_seconds = 0.0
