# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CloseTaskStep(models.Model):
    """
    Month-End Close Task Step - hierarchical structure for v1.2.0 templates.

    Replaces legacy step-baked template codes (CT_X|PREP, CT_X|REVIEW, CT_X|APPROVAL)
    with parent-child Many2many relationship via template_id → step_ids.
    """

    _name = "ipai.close.task.step"
    _description = "Month-End Close Task Step"
    _order = "sequence"

    template_id = fields.Many2one(
        "ipai.close.task.template",
        string="Parent Template",
        required=True,
        ondelete="cascade",
        index=True,
        help="Parent closing template this step belongs to",
    )

    step_code = fields.Selection(
        [
            ("PREP", "Preparation"),
            ("REVIEW", "Review"),
            ("APPROVAL", "Approval"),
            ("FILE_PAY", "File & Pay"),
        ],
        string="Step Code",
        required=True,
        index=True,
        help="Workflow step identifier (PREP, REVIEW, APPROVAL, FILE_PAY)",
    )

    step_name = fields.Char(
        string="Step Name",
        required=True,
        help="Human-readable step name (e.g., 'Preparation Step', 'Review Step')",
    )

    sequence = fields.Integer(
        string="Sequence", default=10, help="Display order (lower numbers appear first)"
    )

    default_employee_code = fields.Char(
        string="Default Assignee (employee code)",
        help="Employee code for default task assignment (e.g., 'RIM', 'CKVC')",
    )

    user_id = fields.Many2one(
        "res.users",
        string="Resolved User",
        compute="_compute_user",
        store=True,
        help="User resolved from employee code via x_employee_code field",
    )

    x_legacy_template_code = fields.Char(
        string="Legacy Template Code",
        help="Original step-baked template code (e.g., 'CT_ADJUSTMENTS|PREP') for migration traceability",
    )

    @api.depends("default_employee_code")
    def _compute_user(self):
        """
        Resolve user from employee code.

        Looks up res.users with matching x_employee_code custom field.
        Used for automatic task assignment during generation.
        """
        Users = self.env["res.users"].sudo()
        for rec in self:
            if rec.default_employee_code:
                rec.user_id = Users.search(
                    [("x_employee_code", "=", rec.default_employee_code)], limit=1
                ).id
            else:
                rec.user_id = False

    _sql_constraints = [
        (
            "unique_template_step",
            "UNIQUE(template_id, step_code)",
            "Each template can only have one instance of each step code (PREP, REVIEW, APPROVAL, FILE_PAY)",
        ),
    ]
