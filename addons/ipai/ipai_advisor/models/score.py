# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AdvisorScore(models.Model):
    """Time-series health scores per category."""

    _name = "advisor.score"
    _description = "Advisor Score Snapshot"
    _order = "as_of desc, category_id"

    category_id = fields.Many2one(
        "advisor.category",
        string="Category",
        required=True,
        index=True,
        ondelete="cascade",
    )
    category_code = fields.Char(
        related="category_id.code",
        store=True,
    )

    # Timestamp
    as_of = fields.Datetime(
        string="As Of",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )

    # Score (0-100)
    score = fields.Integer(
        string="Score",
        required=True,
        help="Health score 0-100 (higher is better)",
    )

    # Breakdown
    open_count = fields.Integer(
        string="Open Recommendations",
    )
    high_count = fields.Integer(
        string="High Priority",
    )
    critical_count = fields.Integer(
        string="Critical",
    )
    resolved_count = fields.Integer(
        string="Resolved (period)",
    )

    # Computation inputs
    inputs_json = fields.Text(
        string="Inputs (JSON)",
        help="Raw data used for score computation",
    )

    @api.model
    def compute_scores(self):
        """Recompute scores for all categories based on current recommendations."""
        categories = self.env["advisor.category"].search([("active", "=", True)])
        Recommendation = self.env["advisor.recommendation"]

        for category in categories:
            recs = Recommendation.search(
                [
                    ("category_id", "=", category.id),
                    ("status", "=", "open"),
                ]
            )

            open_count = len(recs)
            high_count = len(recs.filtered(lambda r: r.severity == "high"))
            critical_count = len(recs.filtered(lambda r: r.severity == "critical"))

            # Score formula: 100 - (critical * 25) - (high * 10) - (open * 2)
            penalty = (critical_count * 25) + (high_count * 10) + (open_count * 2)
            score = max(0, min(100, 100 - penalty))

            self.create(
                {
                    "category_id": category.id,
                    "score": score,
                    "open_count": open_count,
                    "high_count": high_count,
                    "critical_count": critical_count,
                }
            )

        return True

    @api.model
    def get_latest_scores(self):
        """Get the latest score for each category."""
        self.env.cr.execute(
            """
            SELECT DISTINCT ON (category_id)
                category_id, score, open_count, high_count, critical_count, as_of
            FROM advisor_score
            ORDER BY category_id, as_of DESC
        """
        )
        return self.env.cr.dictfetchall()
