from odoo import api, fields, models


class ClosingTemplate(models.Model):
    """Reusable closing checklist template (e.g., Month-End Close, BIR 2550M)."""

    _name = "closing.template"
    _description = "Closing Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, id"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(string="Code", help="Short code, e.g., MEC, BIR-2550M")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    closing_type = fields.Selection(
        [
            ("month_end", "Month-End Close"),
            ("bir_monthly", "BIR Monthly Filing"),
            ("bir_quarterly", "BIR Quarterly Filing"),
            ("bir_annual", "BIR Annual Filing"),
            ("year_end", "Year-End Close"),
            ("custom", "Custom"),
        ],
        string="Closing Type",
        required=True,
        default="month_end",
        tracking=True,
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    line_ids = fields.One2many(
        "closing.template.line", "template_id", string="Template Lines", copy=True,
    )

    line_count = fields.Integer(compute="_compute_line_count", string="Tasks")
    description = fields.Html()

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    def action_generate_task_list(self):
        """Open wizard to generate a task list from this template."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Generate Task List",
            "res_model": "closing.task.list",
            "view_mode": "form",
            "context": {
                "default_template_id": self.id,
                "default_closing_type": self.closing_type,
                "default_company_id": self.company_id.id,
            },
            "target": "current",
        }


class ClosingTemplateLine(models.Model):
    """Individual task definition within a closing template."""

    _name = "closing.template.line"
    _description = "Closing Template Line"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "closing.template", required=True, ondelete="cascade",
    )
    name = fields.Char(required=True)
    code = fields.Char(help="Task code, e.g., MEC-010, BIR-030")
    sequence = fields.Integer(default=10)

    task_type = fields.Selection(
        [
            ("manual", "Manual"),
            ("automated", "Automated"),
            ("approval", "Approval"),
            ("checklist", "Checklist"),
        ],
        default="manual",
        required=True,
    )

    stage = fields.Selection(
        [
            ("preparation", "Preparation"),
            ("review", "Review"),
            ("approval", "Approval"),
            ("report_approval", "Report Approval"),
            ("payment_approval", "Payment Approval"),
            ("filing_payment", "Filing & Payment"),
        ],
        required=True,
        default="preparation",
    )

    # Relative deadline: offset from period_end or bir_deadline
    deadline_reference = fields.Selection(
        [
            ("period_end", "Period End"),
            ("bir_deadline", "BIR Deadline"),
        ],
        default="period_end",
        required=True,
    )
    deadline_offset_days = fields.Integer(
        string="Deadline Offset (days)",
        help="Negative = before reference date, positive = after",
        default=0,
    )

    # Role assignment
    processor_role = fields.Char(
        help="Employee code for processor (who does the work), e.g., BOM",
    )
    responsible_role = fields.Char(
        help="Employee code for responsible (who approves), e.g., RIM",
    )

    # Dependencies
    dependency_codes = fields.Char(
        help="Comma-separated codes of predecessor tasks, e.g., MEC-010,MEC-020",
    )

    planned_hours = fields.Float(default=0.0)
    description = fields.Text()
