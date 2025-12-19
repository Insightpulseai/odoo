# -*- coding: utf-8 -*-
from odoo import models, fields


class AdvisorPlaybook(models.Model):
    """Remediation playbooks for recommendations."""

    _name = "advisor.playbook"
    _description = "Advisor Playbook"
    _order = "name"

    name = fields.Char(
        string="Playbook Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        help="Unique identifier for automation reference",
    )
    active = fields.Boolean(default=True)

    # Content
    description = fields.Text(
        string="Description",
        help="Brief description of what this playbook does",
    )
    steps_md = fields.Text(
        string="Steps (Markdown)",
        help="Step-by-step remediation instructions in Markdown",
    )

    # Automation
    automation_kind = fields.Selection(
        [
            ("none", "Manual Only"),
            ("n8n", "n8n Workflow"),
            ("edge_function", "Supabase Edge Function"),
            ("script", "Shell Script"),
            ("api", "External API"),
        ],
        string="Automation Type",
        default="none",
    )
    automation_ref = fields.Char(
        string="Automation Reference",
        help="n8n workflow ID, edge function name, or script path",
    )
    automation_params = fields.Text(
        string="Parameters (JSON)",
        help="Default parameters for automation",
    )

    # Applicable categories
    category_ids = fields.Many2many(
        "advisor.category",
        string="Applicable Categories",
    )

    # Linked recommendations
    recommendation_ids = fields.One2many(
        "advisor.recommendation",
        "playbook_id",
        string="Recommendations",
    )
    recommendation_count = fields.Integer(
        compute="_compute_recommendation_count",
    )

    def _compute_recommendation_count(self):
        for pb in self:
            pb.recommendation_count = len(pb.recommendation_ids)

    def action_execute(self):
        """Trigger automation execution (placeholder)."""
        self.ensure_one()
        # This would integrate with n8n/edge functions
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Playbook Execution",
                "message": f"Playbook '{self.name}' execution triggered.",
                "type": "info",
            },
        }
