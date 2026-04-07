from odoo import api, fields, models


class ExpenseException(models.Model):
    """Structured expense compliance exception (SAP Concur Exceptions API equivalent).

    Exceptions can be blocking (halt approval) or non-blocking (warning).
    Attached at 3 levels: sheet, line, or allocation.
    """

    _name = "ipai.expense.exception"
    _description = "Expense Compliance Exception"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    exception_code = fields.Char(required=True, index=True, tracking=True)
    message = fields.Text(required=True)

    is_blocking = fields.Boolean(
        default=False,
        help="Blocking exceptions halt the approval workflow until resolved.",
        tracking=True,
    )

    severity = fields.Selection(
        [
            ("info", "Info"),
            ("warning", "Warning"),
            ("error", "Error"),
        ],
        default="warning",
        required=True,
    )

    visibility = fields.Selection(
        [
            ("all", "All"),
            ("employee", "Employee Only"),
            ("manager", "Manager Only"),
            ("processor", "Processor Only"),
        ],
        default="all",
    )

    # 3-level polymorphic attachment (mirrors Concur's report/entry/allocation)
    sheet_id = fields.Many2one(
        "hr.expense.sheet", ondelete="cascade", index=True,
    )
    expense_id = fields.Many2one(
        "hr.expense", ondelete="cascade", index=True,
    )

    # Status
    state = fields.Selection(
        [
            ("new", "New"),
            ("in_process", "In Process"),
            ("resolved", "Resolved"),
            ("waived", "Waived"),
        ],
        default="new",
        required=True,
        tracking=True,
    )

    resolved_by = fields.Many2one("res.users", readonly=True)
    resolved_date = fields.Datetime(readonly=True)
    resolution_note = fields.Text()

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )

    def action_resolve(self):
        self.write({
            "state": "resolved",
            "resolved_by": self.env.uid,
            "resolved_date": fields.Datetime.now(),
        })

    def action_waive(self):
        self.write({
            "state": "waived",
            "resolved_by": self.env.uid,
            "resolved_date": fields.Datetime.now(),
        })
