# -*- coding: utf-8 -*-
"""
IPAI Document Tag Model.

Provides categorization tags for knowledge documents, enabling
filtering and organization of content by topic or theme.
"""
from odoo import fields, models


class IpaiDocTag(models.Model):
    """
    Document Tag Model.

    Simple categorization tags for documents with color coding support.
    Tags can be shared across documents for consistent organization.

    Attributes:
        _name: ipai.doc.tag
        _description: IPAI Doc Tag
    """

    _name = "ipai.doc.tag"
    _description = "IPAI Doc Tag"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer(string="Color Index")
