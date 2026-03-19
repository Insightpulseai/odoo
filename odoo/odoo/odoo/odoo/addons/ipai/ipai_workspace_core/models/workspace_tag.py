# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class WorkspaceTag(models.Model):
    _name = "workspace.tag"
    _description = "Workspace Tag"

    name = fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string="Color Index")
