# -*- coding: utf-8 -*-
"""
pulser.intent — Intent classification taxonomy.

Defines the tri-modal behavior contract: informational, navigational, transactional.
Odoo is always the live-state source; this model configures routing, not ERP truth.
"""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PulserIntent(models.Model):
    _name = "pulser.intent"
    _description = "Pulser Intent Classification"
    _order = "sequence, name"

    name = fields.Char(
        string="Intent Name",
        required=True,
        help="Human-readable label for this intent (e.g. 'Query Invoice Status')",
    )
    sequence = fields.Integer(default=10)
    intent_type = fields.Selection(
        selection=[
            ("informational", "Informational"),
            ("navigational", "Navigational"),
            ("transactional", "Transactional"),
        ],
        string="Intent Type",
        required=True,
        help=(
            "Informational: answers from live Odoo data. "
            "Navigational: guides to Odoo views/menus. "
            "Transactional: executes a bounded action through a safety gate."
        ),
    )
    domain = fields.Char(
        string="Domain",
        help="Owning business domain (e.g. 'expense', 'project', 'hr', 'accounting')",
    )
    description = fields.Text(string="Description")
    example_query = fields.Text(
        string="Example Query",
        help="Representative user utterance for this intent",
    )
    is_active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        (
            "unique_intent_name",
            "UNIQUE(name)",
            "Intent name must be unique.",
        )
    ]

    @api.constrains("intent_type")
    def _check_intent_type(self):
        valid = {"informational", "navigational", "transactional"}
        for rec in self:
            if rec.intent_type not in valid:
                raise ValidationError(
                    f"Invalid intent_type '{rec.intent_type}'. Must be one of: {valid}"
                )
