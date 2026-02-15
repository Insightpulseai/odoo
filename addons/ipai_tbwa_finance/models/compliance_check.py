from odoo import api, fields, models


class ComplianceCheck(models.Model):
    """
    Compliance check results for each closing period.
    Pre-close validations before month can be closed.
    """

    _name = "compliance.check"
    _description = "Compliance Check"
    _order = "closing_id, sequence"

    name = fields.Char(string="Check Name", required=True)
    sequence = fields.Integer(default=10)

    closing_id = fields.Many2one(
        "closing.period",
        string="Closing Period",
        required=True,
        ondelete="cascade",
    )
    check_type = fields.Selection(
        [
            ("gl", "General Ledger"),
            ("ar", "Accounts Receivable"),
            ("ap", "Accounts Payable"),
            ("bank", "Bank Reconciliation"),
            ("tax", "Tax Compliance"),
            ("payroll", "Payroll"),
            ("inventory", "Inventory"),
        ],
        string="Check Type",
        required=True,
    )

    status = fields.Selection(
        [
            ("pending", "Pending"),
            ("passed", "Passed"),
            ("warning", "Warning"),
            ("failed", "Failed"),
        ],
        string="Status",
        default="pending",
    )

    result_text = fields.Text(string="Result Details")
    checked_date = fields.Datetime(string="Last Checked")
    checked_by = fields.Many2one("res.users", string="Checked By")

    # Thresholds
    expected_value = fields.Float(string="Expected")
    actual_value = fields.Float(string="Actual")
    variance = fields.Float(
        string="Variance",
        compute="_compute_variance",
        store=True,
    )
    tolerance = fields.Float(string="Tolerance %", default=0.01)

    @api.depends("expected_value", "actual_value")
    def _compute_variance(self):
        for rec in self:
            if rec.expected_value:
                rec.variance = abs(rec.actual_value - rec.expected_value) / abs(
                    rec.expected_value
                )
            else:
                rec.variance = 0.0

    def action_run_check(self):
        """Execute the compliance check"""
        self.ensure_one()
        # Dispatch to specific check method
        method = f"_check_{self.check_type}"
        if hasattr(self, method):
            getattr(self, method)()
        else:
            self._default_check()

        self.checked_date = fields.Datetime.now()
        self.checked_by = self.env.uid

    def _default_check(self):
        """Default check - mark as pending manual review"""
        self.status = "warning"
        self.result_text = "Manual verification required"

    def _check_gl(self):
        """Check GL is balanced"""
        # Sum of debits = sum of credits
        moves = self.env["account.move"].search(
            [
                ("company_id", "=", self.closing_id.company_id.id),
                ("date", ">=", self.closing_id.period_date.replace(day=1)),
                ("date", "<=", self.closing_id.period_date),
                ("state", "=", "posted"),
            ]
        )
        total_debit = sum(moves.mapped("line_ids.debit"))
        total_credit = sum(moves.mapped("line_ids.credit"))

        self.expected_value = total_debit
        self.actual_value = total_credit
        if abs(total_debit - total_credit) < 0.01:
            self.status = "passed"
            self.result_text = (
                f"GL balanced: Debit={total_debit:,.2f}, Credit={total_credit:,.2f}"
            )
        else:
            self.status = "failed"
            self.result_text = (
                f"GL imbalance: Debit={total_debit:,.2f} ≠ Credit={total_credit:,.2f}"
            )

    def _check_bank(self):
        """Check bank reconciliation status"""
        # Find unreconciled bank statement lines
        unreconciled = self.env["account.bank.statement.line"].search_count(
            [
                ("company_id", "=", self.closing_id.company_id.id),
                ("date", "<=", self.closing_id.period_date),
                ("is_reconciled", "=", False),
            ]
        )

        self.actual_value = unreconciled
        self.expected_value = 0
        if unreconciled == 0:
            self.status = "passed"
            self.result_text = "All bank transactions reconciled"
        elif unreconciled <= 5:
            self.status = "warning"
            self.result_text = f"{unreconciled} unreconciled transactions (minor)"
        else:
            self.status = "failed"
            self.result_text = f"{unreconciled} unreconciled transactions"

    def _check_tax(self):
        """Check tax returns filed"""
        unfiled = self.env["finance.task"].search_count(
            [
                ("closing_id", "=", self.closing_id.id),
                ("task_type", "=", "bir_filing"),
                ("state", "!=", "done"),
            ]
        )

        self.actual_value = unfiled
        self.expected_value = 0
        if unfiled == 0:
            self.status = "passed"
            self.result_text = "All BIR returns filed"
        else:
            self.status = "failed"
            self.result_text = f"{unfiled} BIR returns pending"

    @api.model
    def generate_checks_for_period(self, closing_id):
        """Generate standard compliance checks for a closing period"""
        checks = [
            {"name": "GL Balance Check", "check_type": "gl", "sequence": 10},
            {"name": "Bank Reconciliation", "check_type": "bank", "sequence": 20},
            {"name": "AR Aging Review", "check_type": "ar", "sequence": 30},
            {"name": "AP Accrual Check", "check_type": "ap", "sequence": 40},
            {"name": "BIR Filing Status", "check_type": "tax", "sequence": 50},
            {"name": "Payroll Reconciliation", "check_type": "payroll", "sequence": 60},
        ]
        for check in checks:
            check["closing_id"] = closing_id
            self.create(check)
