# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AdvisorCategory(models.Model):
    """Advisor recommendation categories (Cost, Security, Reliability, etc.)."""

    _name = "advisor.category"
    _description = "Advisor Category"
    _order = "sequence, name"

    name = fields.Char(
        string="Category Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
        help="Unique identifier (e.g., 'cost', 'security', 'reliability')",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    description = fields.Text(string="Description")
    icon = fields.Char(
        string="Icon",
        default="fa-lightbulb-o",
        help="FontAwesome icon class",
    )
    color = fields.Integer(
        string="Color Index",
        default=0,
    )

    # Recommendations in this category
    recommendation_ids = fields.One2many(
        "advisor.recommendation",
        "category_id",
        string="Recommendations",
    )
    recommendation_count = fields.Integer(
        compute="_compute_recommendation_count",
        string="Recommendations",
    )
    open_count = fields.Integer(
        compute="_compute_recommendation_count",
        string="Open",
    )
    high_count = fields.Integer(
        compute="_compute_recommendation_count",
        string="High Priority",
    )

    # Latest score
    latest_score = fields.Integer(
        compute="_compute_latest_score",
        string="Score",
    )

    @api.depends("recommendation_ids", "recommendation_ids.status", "recommendation_ids.severity")
    def _compute_recommendation_count(self):
        for cat in self:
            recs = cat.recommendation_ids
            cat.recommendation_count = len(recs)
            cat.open_count = len(recs.filtered(lambda r: r.status == "open"))
            cat.high_count = len(
                recs.filtered(
                    lambda r: r.status == "open"
                    and r.severity in ("high", "critical")
                )
            )

    def _compute_latest_score(self):
        Score = self.env["advisor.score"]
        for cat in self:
            latest = Score.search([
                ("category_id", "=", cat.id),
            ], order="as_of desc", limit=1)
            cat.latest_score = latest.score if latest else 0

    def action_view_recommendations(self):
        """Open recommendations for this category."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Recommendations - {self.name}",
            "res_model": "advisor.recommendation",
            "view_mode": "list,form",
            "domain": [("category_id", "=", self.id)],
            "context": {
                "default_category_id": self.id,
                "search_default_filter_open": 1,
            },
        }

    _sql_constraints = [
        ("code_unique", "UNIQUE(code)", "Category code must be unique!"),
    ]
