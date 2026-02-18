# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AiLivechat(models.Model):
    _name = "ipai.ai.livechat"
    _description = "AI Livechat"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    notes = fields.Text(string="Notes")

    # TODO: Add specific fields for AI Livechat
