# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTemplates(models.Model):
    _name = "ipai.project.templates"
    _description = "Project Templates"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    notes = fields.Text(string="Notes")

    # TODO: Add specific fields for Project Templates
