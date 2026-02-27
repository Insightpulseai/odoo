# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class IpaiAgentPolicy(models.Model):
    """
    Governance policy for IPAI agent runs.

    Defines per-model (and optionally per-company) defaults:
    - which tools are allowed
    - whether human approval is required before dispatch
    - maximum queue depth before auto-rejection

    There is at most one active policy per (target_model, company_id) pair.
    """

    _name = "ipai.agent.policy"
    _description = "IPAI Agent Policy"
    _order = "company_id, target_model"

    name = fields.Char(
        string="Policy Name",
        required=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )
    target_model = fields.Char(
        string="Target Model",
        required=True,
        help="Odoo model name this policy applies to (e.g. hr.expense.liquidation)",
    )
    require_approval = fields.Boolean(
        string="Require Human Approval",
        default=True,
        help="If set, runs for this model move to 'waiting_approval' before dispatch.",
    )
    allowed_tool_ids = fields.Many2many(
        "ipai.agent.tool",
        "agent_policy_tool_rel",
        "policy_id",
        "tool_id",
        string="Allowed Tools",
        help="Restrict which tools may be called in runs governed by this policy.",
    )
    max_queue_depth = fields.Integer(
        string="Max Queue Depth",
        default=10,
        help="Auto-reject new runs when this many queued/running runs exist for the model.",
    )
    notes = fields.Text(string="Notes")

    @api.constrains("target_model", "company_id", "active")
    def _check_unique_active_policy(self):
        for rec in self:
            if not rec.active:
                continue
            duplicate = self.search([
                ("target_model", "=", rec.target_model),
                ("company_id", "=", rec.company_id.id),
                ("active", "=", True),
                ("id", "!=", rec.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "An active policy for model '%s' (company: %s) already exists: '%s'."
                ) % (rec.target_model, rec.company_id.name, duplicate.name))

    @api.model
    def get_policy_for(self, model_name, company_id=None):
        """
        Return the active policy governing runs on `model_name` for the given company,
        or False if none is configured.
        """
        company_id = company_id or self.env.company.id
        return self.search([
            ("target_model", "=", model_name),
            ("company_id", "=", company_id),
            ("active", "=", True),
        ], limit=1)
