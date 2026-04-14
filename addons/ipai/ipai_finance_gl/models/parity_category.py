# © 2026 InsightPulseAI — License: LGPL-3
"""
ipai.finance.gl.parity.category
--------------------------------
Taxonomy for D365 Finance GL parity records.

Each category represents a functional grouping of D365 GL concepts
(e.g. chart-of-accounts, fiscal-calendar, journal, financial-dimensions).
Categories are referenced by parity records and drive filtering/reporting
in the parity-matrix view.
"""

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FinanceGlParityCategory(models.Model):
    """Taxonomy grouping for D365 Finance GL parity concepts."""

    _name = "ipai.finance.gl.parity.category"
    _description = "D365 Finance GL Parity Category"
    _inherit = ["mail.thread"]
    _rec_name = "name"
    _order = "sequence, name"

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------

    name = fields.Char(
        string="Category Name",
        required=True,
        tracking=True,
        help="Human-readable name, e.g. 'Chart of Accounts', 'Fiscal Calendar'.",
    )
    code = fields.Char(
        string="Code",
        required=True,
        tracking=True,
        help="Short slug used in data files and exports, e.g. 'chart-of-accounts'.",
    )
    description = fields.Text(
        string="Description",
        help="Narrative description of the D365 GL functional area this category covers.",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Display ordering within the parity matrix.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
        help="Archived categories are hidden from parity views but retained for history.",
    )

    # -------------------------------------------------------------------------
    # SQL constraints
    # -------------------------------------------------------------------------

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name)",
            "A parity category with this name already exists. Category names must be unique.",
        ),
        (
            "code_uniq",
            "unique(code)",
            "A parity category with this code already exists. Category codes must be unique.",
        ),
    ]
