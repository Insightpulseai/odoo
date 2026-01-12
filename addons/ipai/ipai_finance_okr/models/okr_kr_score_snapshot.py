# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OkrKrScoreSnapshot(models.Model):
    """Time series of KR scores for tracking progress over time.

    Record weekly or monthly score snapshots to track OKR progress
    and build historical trend data.
    """

    _name = "okr.kr.score.snapshot"
    _description = "KR Score Snapshot"
    _order = "date desc, id desc"

    key_result_id = fields.Many2one(
        "okr.key.result",
        string="Key Result",
        required=True,
        ondelete="cascade",
    )
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
    )
    score = fields.Float(
        string="Score (0-1.0)",
        required=True,
        digits=(3, 2),
    )
    confidence = fields.Integer(
        string="Confidence (0-100)",
    )
    current_value = fields.Float(
        string="Current Value",
        digits=(12, 2),
        help="The actual measured value at this point in time",
    )
    comment = fields.Text(
        string="Comment",
        help="Notes on the score or any blockers",
    )
    recorded_by_id = fields.Many2one(
        "res.users",
        string="Recorded By",
        default=lambda self: self.env.user,
    )

    # Related fields
    objective_id = fields.Many2one(
        related="key_result_id.objective_id",
        store=True,
    )
    company_id = fields.Many2one(
        related="key_result_id.company_id",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Update the parent KR score when snapshot is created."""
        records = super().create(vals_list)
        for rec in records:
            if rec.key_result_id:
                rec.key_result_id.write({
                    "status_score": rec.score,
                    "confidence": rec.confidence or rec.key_result_id.confidence,
                    "current_value": rec.current_value or rec.key_result_id.current_value,
                })
        return records
