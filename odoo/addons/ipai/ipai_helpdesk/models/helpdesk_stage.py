# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.

from odoo import models, fields


class HelpdeskStage(models.Model):
    """Stages for helpdesk ticket workflow."""

    _name = "ipai.helpdesk.stage"
    _description = "Helpdesk Stage"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Stage Type
    is_close = fields.Boolean(
        string="Closing Stage",
        help="Tickets in this stage are considered closed",
    )
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="This stage will be folded in the Kanban view",
    )

    # Teams
    team_ids = fields.Many2many(
        "ipai.helpdesk.team",
        string="Teams",
        help="Teams that use this stage",
    )

    # Description
    description = fields.Text(
        string="Description",
        help="Description of what this stage represents",
    )

    # Template for Email
    template_id = fields.Many2one(
        "mail.template",
        string="Email Template",
        domain="[('model', '=', 'ipai.helpdesk.ticket')]",
        help="Email template to send when ticket enters this stage",
    )
