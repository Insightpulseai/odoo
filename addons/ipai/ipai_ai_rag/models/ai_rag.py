# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AiRag(models.Model):
    _name = "ipai.ai.rag"
    _description = "AI RAG Pipeline"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    notes = fields.Text(string="Notes")

    # TODO: Add specific fields for AI RAG Pipeline
