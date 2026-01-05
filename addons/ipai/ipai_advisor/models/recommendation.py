# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models


class AdvisorRecommendation(models.Model):
    """Individual recommendations from the Advisor engine."""

    _name = "advisor.recommendation"
    _description = "Advisor Recommendation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "severity_order desc, impact_score desc, create_date desc"

    name = fields.Char(
        string="Title",
        required=True,
        tracking=True,
    )

    # Category (Cost/Security/Reliability/OpsEx/Performance)
    category_id = fields.Many2one(
        "advisor.category",
        string="Category",
        required=True,
        index=True,
        tracking=True,
    )
    category_code = fields.Char(
        related="category_id.code",
        store=True,
    )

    # Severity
    severity = fields.Selection(
        [
            ("info", "Info"),
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Severity",
        required=True,
        default="medium",
        tracking=True,
    )
    severity_order = fields.Integer(
        compute="_compute_severity_order",
        store=True,
    )

    # Impact assessment
    impact_score = fields.Integer(
        string="Impact Score",
        default=50,
        help="0-100 impact score for prioritization",
    )
    estimated_savings = fields.Monetary(
        string="Est. Savings",
        currency_field="currency_id",
        help="Estimated cost savings if resolved (for Cost category)",
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )
    confidence = fields.Float(
        string="Confidence %",
        default=80.0,
        help="Confidence level in this recommendation",
    )

    # Description
    description = fields.Text(
        string="Description",
        help="Detailed explanation of the recommendation",
    )

    # Resource identification
    resource_type = fields.Char(
        string="Resource Type",
        help="Type of affected resource (e.g., 'odoo.model', 'k8s.deployment')",
    )
    resource_ref = fields.Char(
        string="Resource Reference",
        help="Specific resource identifier",
    )
    source = fields.Selection(
        [
            ("k8s", "Kubernetes"),
            ("odoo", "Odoo"),
            ("supabase", "Supabase"),
            ("github", "GitHub/CI"),
            ("ingress", "Ingress/Network"),
            ("manual", "Manual"),
            ("api", "External API"),
        ],
        string="Source",
        default="manual",
    )

    # Evidence
    evidence = fields.Text(
        string="Evidence (JSON)",
        help="JSON evidence supporting this recommendation",
    )

    # Remediation
    playbook_id = fields.Many2one(
        "advisor.playbook",
        string="Playbook",
        help="Linked remediation playbook",
    )
    remediation_steps = fields.Text(
        string="Remediation Steps",
        help="Quick remediation instructions",
    )
    external_link = fields.Char(
        string="External Link",
        help="Link to documentation or runbook",
    )

    # Ownership
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        tracking=True,
    )

    # Status
    status = fields.Selection(
        [
            ("open", "Open"),
            ("acknowledged", "Acknowledged"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
            ("snoozed", "Snoozed"),
            ("dismissed", "Dismissed"),
        ],
        string="Status",
        default="open",
        tracking=True,
    )
    date_due = fields.Date(string="Due Date")
    date_resolved = fields.Date(string="Resolved Date")
    snooze_until = fields.Date(string="Snoozed Until")

    # Tags for filtering
    tag_ids = fields.Many2many(
        "advisor.tag",
        string="Tags",
    )

    @api.depends("severity")
    def _compute_severity_order(self):
        severity_map = {
            "info": 1,
            "low": 2,
            "medium": 3,
            "high": 4,
            "critical": 5,
        }
        for rec in self:
            rec.severity_order = severity_map.get(rec.severity, 0)

    def action_acknowledge(self):
        self.write({"status": "acknowledged"})

    def action_start(self):
        self.write({"status": "in_progress"})

    def action_resolve(self):
        self.write(
            {
                "status": "resolved",
                "date_resolved": fields.Date.context_today(self),
            }
        )

    def action_snooze(self):
        """Snooze for 7 days by default."""
        self.write(
            {
                "status": "snoozed",
                "snooze_until": fields.Date.add(
                    fields.Date.context_today(self), days=7
                ),
            }
        )

    def action_dismiss(self):
        self.write({"status": "dismissed"})

    def action_reopen(self):
        self.write(
            {
                "status": "open",
                "date_resolved": False,
                "snooze_until": False,
            }
        )

    @api.model
    def create_from_signal(self, signal_data):
        """Create recommendation from external signal (n8n webhook)."""
        category = self.env["advisor.category"].search(
            [
                ("code", "=", signal_data.get("category", "ops")),
            ],
            limit=1,
        )

        if not category:
            category = self.env["advisor.category"].search([], limit=1)

        vals = {
            "name": signal_data.get("title", "Unnamed Recommendation"),
            "category_id": category.id,
            "severity": signal_data.get("severity", "medium"),
            "description": signal_data.get("description", ""),
            "resource_type": signal_data.get("resource_type"),
            "resource_ref": signal_data.get("resource_ref"),
            "source": signal_data.get("source", "api"),
            "evidence": json.dumps(signal_data.get("evidence", {})),
            "impact_score": signal_data.get("impact_score", 50),
        }

        return self.create(vals)


class AdvisorTag(models.Model):
    """Tags for recommendation filtering."""

    _name = "advisor.tag"
    _description = "Advisor Tag"
    _order = "name"

    name = fields.Char(string="Tag", required=True)
    color = fields.Integer(string="Color Index", default=0)

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "Tag name must be unique!"),
    ]
