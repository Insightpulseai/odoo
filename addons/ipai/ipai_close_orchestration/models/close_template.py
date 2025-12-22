# -*- coding: utf-8 -*-
"""
Close Task Template

Reusable template for close tasks (maps from A1 Templates).
"""
from odoo import api, fields, models


class CloseTaskTemplate(models.Model):
    """
    Template for generating close tasks.

    Bridged from A1 Templates.
    """

    _name = "close.task.template"
    _description = "Close Task Template"
    _order = "sequence, code"

    _sql_constraints = [
        (
            "code_uniq",
            "unique(code, company_id)",
            "Template code must be unique per company.",
        ),
    ]

    # Core fields
    code = fields.Char(
        string="Code",
        required=True,
        index=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)

    # Category
    category_id = fields.Many2one(
        "close.task.category",
        string="Category",
        ondelete="cascade",
        index=True,
    )

    # Roles (using selection for common roles)
    preparer_role = fields.Selection(
        [
            ("rim", "RIM"),
            ("jpal", "JPAL"),
            ("bom", "BOM"),
            ("ckvc", "CKVC"),
            ("jli", "JLI"),
            ("jap", "JAP"),
            ("las", "LAS"),
            ("rmqb", "RMQB"),
            ("fd", "FD"),
        ],
        string="Preparer Role",
    )

    reviewer_role = fields.Selection(
        [
            ("rim", "RIM"),
            ("jpal", "JPAL"),
            ("bom", "BOM"),
            ("ckvc", "CKVC"),
            ("jli", "JLI"),
            ("jap", "JAP"),
            ("las", "LAS"),
            ("rmqb", "RMQB"),
            ("fd", "FD"),
        ],
        string="Reviewer Role",
    )

    approver_role = fields.Selection(
        [
            ("rim", "RIM"),
            ("jpal", "JPAL"),
            ("bom", "BOM"),
            ("ckvc", "CKVC"),
            ("jli", "JLI"),
            ("jap", "JAP"),
            ("las", "LAS"),
            ("rmqb", "RMQB"),
            ("fd", "FD"),
        ],
        string="Approver Role",
    )

    # Default assignees
    preparer_id = fields.Many2one("res.users", string="Default Preparer")
    reviewer_id = fields.Many2one("res.users", string="Default Reviewer")
    approver_id = fields.Many2one("res.users", string="Default Approver")

    # Effort
    prep_days = fields.Float(string="Prep Days", default=1.0)
    review_days = fields.Float(string="Review Days", default=0.5)
    approval_days = fields.Float(string="Approval Days", default=0.5)

    # Deadline offsets (days before period end)
    prep_offset = fields.Integer(string="Prep Offset", default=-3)
    review_offset = fields.Integer(string="Review Offset", default=-2)
    approval_offset = fields.Integer(string="Approval Offset", default=-1)

    # Checklist
    checklist_ids = fields.One2many(
        "close.task.template.checklist",
        "template_id",
        string="Checklist Items",
    )

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Bridge to A1
    a1_template_id = fields.Many2one(
        "a1.template",
        string="A1 Template",
        help="Source template from A1 Control Center",
    )

    description = fields.Html(string="Description")


class CloseTaskTemplateChecklist(models.Model):
    """
    Checklist item template.
    """

    _name = "close.task.template.checklist"
    _description = "Close Task Template Checklist"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "close.task.template",
        string="Template",
        required=True,
        ondelete="cascade",
    )
    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    is_required = fields.Boolean(string="Required", default=True)
    instructions = fields.Text(string="Instructions")
