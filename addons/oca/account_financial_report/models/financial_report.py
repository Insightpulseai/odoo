# Copyright 2024-2026 InsightPulse AI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_round


class FinancialReport(models.Model):
    """Financial Report Definition."""

    _name = "account.financial.report"
    _description = "Financial Report"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    parent_id = fields.Many2one(
        "account.financial.report",
        string="Parent Report",
    )
    child_ids = fields.One2many(
        "account.financial.report",
        "parent_id",
        string="Child Reports",
    )
    level = fields.Integer(compute="_compute_level", store=True)
    report_type = fields.Selection(
        [
            ("sum", "Sum of Children"),
            ("accounts", "Account Balances"),
            ("account_type", "By Account Type"),
            ("report_value", "Report Value"),
        ],
        default="sum",
        required=True,
    )
    account_ids = fields.Many2many(
        "account.account",
        string="Accounts",
        help="Accounts to include when report_type is 'accounts'",
    )
    account_type_ids = fields.Many2many(
        "account.account.type",
        string="Account Types",
        help="Account types to include when report_type is 'account_type'",
    )
    sign = fields.Selection(
        [("-1", "Reverse Balance Sign"), ("1", "Normal Balance Sign")],
        default="1",
        required=True,
    )
    display_detail = fields.Selection(
        [
            ("no_detail", "No Detail"),
            ("detail_flat", "Display Accounts"),
            ("detail_with_hierarchy", "Display Hierarchy"),
        ],
        default="no_detail",
    )
    style_overwrite = fields.Selection(
        [
            ("0", "Automatic"),
            ("1", "Main Title 1 (Bold, Big)"),
            ("2", "Main Title 2 (Bold, Medium)"),
            ("3", "Sub Title (Bold, Small)"),
            ("4", "Normal"),
            ("5", "Italic"),
            ("6", "Smallest (Small)"),
        ],
        default="0",
    )

    @api.depends("parent_id", "parent_id.level")
    def _compute_level(self):
        for report in self:
            if report.parent_id:
                report.level = report.parent_id.level + 1
            else:
                report.level = 0


class FinancialReportWizard(models.TransientModel):
    """Wizard for generating financial reports."""

    _name = "account.financial.report.wizard"
    _description = "Financial Report Wizard"

    report_id = fields.Many2one(
        "account.financial.report",
        string="Report",
        required=True,
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    target_move = fields.Selection(
        [("posted", "Posted Entries Only"), ("all", "All Entries")],
        default="posted",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    debit_credit = fields.Boolean(
        string="Show Debit/Credit Columns",
        default=True,
    )
    enable_filter = fields.Boolean(string="Enable Comparison")
    filter_date_from = fields.Date(string="Comparison Date From")
    filter_date_to = fields.Date(string="Comparison Date To")

    def _get_account_balance(self, accounts, date_from, date_to, target_move):
        """Get balance for accounts in date range."""
        domain = [
            ("account_id", "in", accounts.ids),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ]
        if target_move == "posted":
            domain.append(("parent_state", "=", "posted"))

        result = {"debit": 0.0, "credit": 0.0, "balance": 0.0}
        for line in self.env["account.move.line"].search(domain):
            result["debit"] += line.debit
            result["credit"] += line.credit
            result["balance"] += line.balance

        return result

    def _compute_report_balance(self, report):
        """Compute balance for a financial report line."""
        result = {"debit": 0.0, "credit": 0.0, "balance": 0.0}

        if report.report_type == "accounts":
            res = self._get_account_balance(
                report.account_ids,
                self.date_from,
                self.date_to,
                self.target_move,
            )
            result["debit"] = res["debit"]
            result["credit"] = res["credit"]
            result["balance"] = res["balance"] * int(report.sign)

        elif report.report_type == "account_type":
            accounts = self.env["account.account"].search(
                [("account_type", "in", report.account_type_ids.ids)]
            )
            res = self._get_account_balance(
                accounts,
                self.date_from,
                self.date_to,
                self.target_move,
            )
            result["debit"] = res["debit"]
            result["credit"] = res["credit"]
            result["balance"] = res["balance"] * int(report.sign)

        elif report.report_type == "sum":
            for child in report.child_ids:
                child_res = self._compute_report_balance(child)
                result["debit"] += child_res["debit"]
                result["credit"] += child_res["credit"]
                result["balance"] += child_res["balance"]

        return result

    def action_view_report(self):
        """Generate and display the financial report."""
        self.ensure_one()

        # Compute report data
        report_lines = []
        for report in self.report_id | self.report_id.child_ids:
            balance = self._compute_report_balance(report)
            report_lines.append(
                {
                    "name": report.name,
                    "level": report.level,
                    "debit": float_round(balance["debit"], 2),
                    "credit": float_round(balance["credit"], 2),
                    "balance": float_round(balance["balance"], 2),
                }
            )

        # Return action to display report
        return {
            "type": "ir.actions.act_window",
            "name": self.report_id.name,
            "res_model": "account.financial.report.line",
            "view_mode": "list",
            "target": "current",
            "context": {
                "report_lines": report_lines,
                "date_from": self.date_from.isoformat(),
                "date_to": self.date_to.isoformat(),
            },
        }

    def action_export_pdf(self):
        """Export financial report to PDF."""
        return self.env.ref(
            "account_financial_report.action_report_financial"
        ).report_action(self)

    def action_export_xlsx(self):
        """Export financial report to Excel."""
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Export",
                "message": "Excel export functionality available via Superset integration",
                "type": "info",
            },
        }
