# -*- coding: utf-8 -*-
"""
pulser.action.class — Safe action gate classification.

All transactional Pulser actions must be classified before execution.
No unclassified transactional action may execute (Constitution Principle 4).
"""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PulserActionClass(models.Model):
    _name = "pulser.action.class"
    _description = "Pulser Action Class"
    _order = "name"

    name = fields.Char(string="Class Name", required=True)
    class_type = fields.Selection(
        selection=[
            ("advisory", "Advisory"),
            ("approval_gated", "Approval-Gated"),
            ("auto_routable", "Auto-Routable"),
        ],
        string="Class Type",
        required=True,
        help=(
            "Advisory: suggest/preview only, no state change. "
            "Approval-Gated: propose action, human must confirm. "
            "Auto-Routable: low-risk, policy-compliant, auto-executes with audit log."
        ),
    )
    description = fields.Text(string="Description")
    requires_approval = fields.Boolean(
        string="Requires Approval",
        compute="_compute_requires_approval",
        store=True,
        readonly=True,
        help="Derived from class_type. Approval-gated classes always require approval.",
    )
    max_auto_route_level = fields.Integer(
        string="Max Auto-Route Level",
        default=0,
        help=(
            "Risk ceiling for auto-routing. 0=no auto-route, 1=low-risk, 2=medium-risk. "
            "Only meaningful for auto_routable class type."
        ),
    )

    _sql_constraints = [
        (
            "unique_class_name",
            "UNIQUE(name)",
            "Action class name must be unique.",
        )
    ]

    @api.depends("class_type")
    def _compute_requires_approval(self):
        for rec in self:
            rec.requires_approval = rec.class_type == "approval_gated"

    @api.constrains("class_type", "max_auto_route_level")
    def _check_auto_route_level(self):
        for rec in self:
            if rec.class_type != "auto_routable" and rec.max_auto_route_level > 0:
                raise ValidationError(
                    "max_auto_route_level must be 0 for non-auto_routable action classes."
                )
            if rec.max_auto_route_level < 0:
                raise ValidationError(
                    "max_auto_route_level cannot be negative."
                )
