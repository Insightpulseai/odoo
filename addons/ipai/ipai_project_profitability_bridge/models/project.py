# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    ipai_profitability_id = fields.Many2one(
        "ipai.project.profitability",
        string="Profitability Record",
        compute="_compute_ipai_profitability",
    )
    ipai_margin = fields.Monetary(
        string="Margin (IPAI)",
        compute="_compute_ipai_profitability",
        currency_field="currency_id",
    )
    ipai_margin_pct = fields.Float(
        string="Margin % (IPAI)",
        compute="_compute_ipai_profitability",
    )
    ipai_revenue = fields.Monetary(
        string="Revenue (IPAI)",
        compute="_compute_ipai_profitability",
        currency_field="currency_id",
    )
    ipai_cost = fields.Monetary(
        string="Cost (IPAI)",
        compute="_compute_ipai_profitability",
        currency_field="currency_id",
    )

    @api.depends("id")
    def _compute_ipai_profitability(self):
        Profitability = self.env["ipai.project.profitability"]
        for project in self:
            rec = Profitability.search(
                [
                    ("project_id", "=", project.id),
                    ("company_id", "=", project.company_id.id),
                ],
                limit=1,
            )
            project.ipai_profitability_id = rec.id if rec else False
            project.ipai_margin = rec.margin if rec else 0.0
            project.ipai_margin_pct = rec.margin_pct if rec else 0.0
            project.ipai_revenue = rec.revenue if rec else 0.0
            project.ipai_cost = rec.cost if rec else 0.0

    def action_recompute_profitability(self):
        """Button action to recompute profitability for selected projects."""
        Profitability = self.env["ipai.project.profitability"]
        for project in self:
            Profitability.recompute_for_project(project.id)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Profitability Updated",
                "message": f"Updated profitability for {len(self)} project(s).",
                "type": "success",
                "sticky": False,
            },
        }
