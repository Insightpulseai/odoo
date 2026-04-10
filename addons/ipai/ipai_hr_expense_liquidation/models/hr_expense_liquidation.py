# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrExpenseLiquidation(models.Model):
    """
    Expense Liquidation Model with Cash Advance Tracking

    Supports 3 liquidation types:
    - Cash Advance: Employee receives advance, liquidates with itemized expenses
    - Reimbursement: Employee pays out-of-pocket, submits for reimbursement
    - Petty Cash: Small purchases from petty cash fund

    Features:
    - Itemized expense lines with bucket categorization
    - Automatic bucket totals (Meals, Transportation, Misc)
    - Cash advance settlement calculations
    - Multi-currency support
    - Extended 8-state approval workflow (cash advance lifecycle)
    - Accounting entries with idempotency
    - Policy engine with configurable rules
    - Monitoring cron for overdue advances
    """

    _name = "hr.expense.liquidation"
    _description = "Expense Liquidation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        default=lambda self: _("New"),
        copy=False,
    )

    # Liquidation Type
    liquidation_type = fields.Selection(
        [
            ("cash_advance", "Cash Advance"),
            ("reimbursement", "Reimbursement"),
            ("petty_cash", "Petty Cash"),
        ],
        string="Liquidation Type",
        required=True,
        default="cash_advance",
        tracking=True,
        help="Cash Advance: Settle advance with expenses | "
             "Reimbursement: Reimburse out-of-pocket expenses | "
             "Petty Cash: Small purchases from petty cash fund"
    )

    # Employee Info
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    # Dates
    date = fields.Date(
        string="Liquidation Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    period_start = fields.Date(string="Period Start")
    period_end = fields.Date(string="Period End")
    liquidation_report_date = fields.Date(
        string="Date Prepared",
        default=fields.Date.context_today,
        help="Date the liquidation report was prepared (TBWA report header)",
    )

    # Currency
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    # Cash Advance (for cash_advance type)
    advance_amount = fields.Monetary(
        string="Advance Amount",
        currency_field="currency_id",
        tracking=True,
        help="Cash advance received by employee"
    )
    advance_reference = fields.Char(string="Advance Reference")
    advance_date = fields.Date(string="Advance Date")

    # Cash Advance Request link
    cash_advance_request_id = fields.Many2one(
        "cash.advance",
        string="Cash Advance Request",
        readonly=True,
        copy=False,
    )

    # Branch
    branch_id = fields.Many2one(
        "operating.branch",
        string="Branch",
    )

    # Client / Cost Element
    client_name = fields.Char(string="Client Name")
    ce_number = fields.Char(string="Cost Element Number")
    form_no = fields.Char(
        string="Form No.",
        help="Manual form number override for printed reports",
    )

    # Expense Lines
    line_ids = fields.One2many(
        "hr.expense.liquidation.line",
        "liquidation_id",
        string="Expense Lines",
        copy=True,
    )
    line_count = fields.Integer(compute="_compute_line_count", string="Line Count")

    # Bucket Totals
    total_meals = fields.Monetary(
        string="Meals & Entertainment",
        currency_field="currency_id",
        compute="_compute_bucket_totals",
        store=True,
        help="Total expenses for meals and entertainment"
    )
    total_transportation = fields.Monetary(
        string="Transportation & Travel",
        currency_field="currency_id",
        compute="_compute_bucket_totals",
        store=True,
        help="Total expenses for transportation and travel"
    )
    total_miscellaneous = fields.Monetary(
        string="Miscellaneous",
        currency_field="currency_id",
        compute="_compute_bucket_totals",
        store=True,
        help="Other miscellaneous expenses"
    )

    # Totals
    total_expenses = fields.Monetary(
        string="Total Expenses",
        currency_field="currency_id",
        compute="_compute_totals",
        store=True,
    )

    # Withholding / Net
    gross_amount = fields.Monetary(
        string="Gross Amount",
        currency_field="currency_id",
        help="Gross amount before withholding tax (for tax context)",
    )
    withholding_tax_amount = fields.Monetary(
        string="Withholding Tax",
        currency_field="currency_id",
    )
    net_paid_amount = fields.Monetary(
        string="Net Paid Amount",
        currency_field="currency_id",
        compute="_compute_net_paid_amount",
        store=True,
    )

    # Multi-page
    other_pages_total = fields.Monetary(
        string="Other Pages Total",
        currency_field="currency_id",
        help="Total from additional pages of the liquidation report",
    )
    grand_total = fields.Monetary(
        string="Grand Total",
        currency_field="currency_id",
        compute="_compute_grand_total",
        store=True,
    )

    # Settlement
    settlement_amount = fields.Monetary(
        string="Settlement Amount",
        currency_field="currency_id",
        compute="_compute_settlement",
        store=True,
        help="Positive: Return to company | Negative: Additional reimbursement to employee"
    )
    settlement_status = fields.Selection(
        [
            ("return", "Return to Company"),
            ("balanced", "Balanced"),
            ("reimburse", "Reimburse Employee"),
        ],
        string="Settlement Status",
        compute="_compute_settlement",
        store=True,
    )
    amount_due_to_employee = fields.Monetary(
        string="Amount Due to Employee",
        currency_field="currency_id",
        compute="_compute_settlement",
        store=True,
    )
    amount_refundable_to_company = fields.Monetary(
        string="Amount Refundable to Company",
        currency_field="currency_id",
        compute="_compute_settlement",
        store=True,
    )

    # Extended Approval Workflow (cash advance lifecycle)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("manager_approved", "Manager Approved"),
            ("finance_approved", "Finance Approved"),
            ("released", "Released"),
            ("in_liquidation", "In Liquidation"),
            ("liquidated", "Liquidated"),
            ("closed", "Closed"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        tracking=True,
    )
    approval_date = fields.Datetime(string="Approval Date", readonly=True)
    finance_approver_id = fields.Many2one(
        "res.users",
        string="Finance Approver",
        tracking=True,
    )
    finance_approval_date = fields.Datetime(string="Finance Approval Date", readonly=True)

    # Submitted / Posted by
    submitted_by_name = fields.Char(
        string="Submitted By",
        help="Name of the person who submitted the liquidation report",
    )
    finance_posted_by = fields.Many2one(
        "res.users",
        string="Finance Posted By",
        readonly=True,
    )
    finance_reviewed_by = fields.Many2one(
        "res.users",
        string="Finance Reviewed By",
        readonly=True,
    )

    # Accounting entries
    release_move_id = fields.Many2one(
        "account.move",
        string="Release Journal Entry",
        readonly=True,
        copy=False,
    )
    liquidation_move_id = fields.Many2one(
        "account.move",
        string="Liquidation Journal Entry",
        readonly=True,
        copy=False,
    )

    # Policy
    policy_exception_ids = fields.One2many(
        "hr.expense.policy.violation",
        "liquidation_id",
        string="Policy Violations",
    )
    policy_exception_count = fields.Integer(
        compute="_compute_policy_exception_count",
        string="Violations",
    )

    # Notes
    description = fields.Text(string="Purpose/Description")
    notes = fields.Text(string="Internal Notes")

    # ── Compute methods ──────────────────────────────────────────────────────

    @api.depends("line_ids")
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    @api.depends("line_ids.amount", "line_ids.bucket")
    def _compute_bucket_totals(self):
        for record in self:
            record.total_meals = sum(
                line.amount for line in record.line_ids if line.bucket == "meals"
            )
            record.total_transportation = sum(
                line.amount for line in record.line_ids if line.bucket == "transportation"
            )
            record.total_miscellaneous = sum(
                line.amount for line in record.line_ids if line.bucket == "miscellaneous"
            )

    @api.depends("line_ids.amount")
    def _compute_totals(self):
        for record in self:
            record.total_expenses = sum(record.line_ids.mapped("amount"))

    @api.depends("gross_amount", "withholding_tax_amount")
    def _compute_net_paid_amount(self):
        for record in self:
            record.net_paid_amount = record.gross_amount - record.withholding_tax_amount

    @api.depends("total_expenses", "other_pages_total")
    def _compute_grand_total(self):
        for record in self:
            record.grand_total = record.total_expenses + record.other_pages_total

    @api.depends("liquidation_type", "advance_amount", "total_expenses")
    def _compute_settlement(self):
        for record in self:
            if record.liquidation_type == "cash_advance":
                # Positive = Return | Negative = Additional reimbursement
                record.settlement_amount = record.advance_amount - record.total_expenses

                if record.settlement_amount > 0:
                    record.settlement_status = "return"
                    record.amount_refundable_to_company = record.settlement_amount
                    record.amount_due_to_employee = 0.0
                elif record.settlement_amount < 0:
                    record.settlement_status = "reimburse"
                    record.amount_due_to_employee = abs(record.settlement_amount)
                    record.amount_refundable_to_company = 0.0
                else:
                    record.settlement_status = "balanced"
                    record.amount_due_to_employee = 0.0
                    record.amount_refundable_to_company = 0.0
            else:
                # Reimbursement or Petty Cash: no settlement, just total
                record.settlement_amount = 0.0
                record.settlement_status = "balanced"
                record.amount_due_to_employee = 0.0
                record.amount_refundable_to_company = 0.0

    @api.depends("policy_exception_ids")
    def _compute_policy_exception_count(self):
        for record in self:
            record.policy_exception_count = len(record.policy_exception_ids)

    # ── Constraints ──────────────────────────────────────────────────────────

    @api.constrains("employee_id", "company_id")
    def _check_linked_expenses_scope(self):
        """
        Guard against cross-entity drift: any hr.expense records that reference
        this liquidation must share the same employee and company.
        Called on create/write of employee_id or company_id.
        """
        for rec in self:
            linked = self.env["hr.expense"].search(
                [("cash_advance_liquidation_id", "=", rec.id)], limit=50
            )
            bad_emp = linked.filtered(lambda e: e.employee_id != rec.employee_id)
            if bad_emp:
                raise ValidationError(_(
                    "Expense(s) '%s' belong to a different employee "
                    "and cannot be linked to this liquidation (%s).",
                    ", ".join(bad_emp.mapped("name")),
                    rec.employee_id.name,
                ))
            bad_company = linked.filtered(lambda e: e.company_id != rec.company_id)
            if bad_company:
                raise ValidationError(_(
                    "Expense(s) '%s' belong to a different company "
                    "and cannot be linked to this liquidation.",
                    ", ".join(bad_company.mapped("name")),
                ))

    # ── CRUD overrides ───────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("hr.expense.liquidation")
                    or _("New")
                )
        return super().create(vals_list)

    # ── State transitions ────────────────────────────────────────────────────

    def action_submit(self):
        self.ensure_one()
        if not self.line_ids and self.liquidation_type != "cash_advance":
            raise ValidationError(_("Cannot submit liquidation without expense lines."))
        self.write({"state": "submitted"})
        self.message_post(body=_("Cash advance request submitted for approval."))

    def action_manager_approve(self):
        self.ensure_one()
        if self.state != "submitted":
            raise ValidationError(_("Only submitted requests can be manager-approved."))
        self.write({
            "state": "manager_approved",
            "approver_id": self.env.user.id,
            "approval_date": fields.Datetime.now(),
        })
        self.message_post(body=_("Manager approved by %s.", self.env.user.name))

    def action_finance_approve(self):
        self.ensure_one()
        if self.state != "manager_approved":
            raise ValidationError(_("Only manager-approved requests can be finance-approved."))
        self.write({
            "state": "finance_approved",
            "finance_approver_id": self.env.user.id,
            "finance_approval_date": fields.Datetime.now(),
        })
        self.message_post(body=_("Finance approved by %s.", self.env.user.name))

    def action_release(self):
        """Release cash advance funds. Creates idempotent accounting entry."""
        for rec in self:
            if rec.state != "finance_approved":
                raise ValidationError(_("Only finance-approved requests can be released."))
            key = "CA-RELEASE-%s" % rec.name
            existing = self.env["account.move"].search([("ref", "=", key)], limit=1)
            if existing:
                rec.release_move_id = existing
            else:
                journal = self.env["account.journal"].search(
                    [("type", "=", "general"), ("company_id", "=", rec.company_id.id)],
                    limit=1,
                )
                if not journal:
                    raise ValidationError(_(
                        "No general journal found for company %s. "
                        "Please configure a Miscellaneous journal.",
                        rec.company_id.name,
                    ))
                move = self.env["account.move"].create({
                    "ref": key,
                    "journal_id": journal.id,
                    "move_type": "entry",
                    "date": fields.Date.context_today(self),
                })
                rec.release_move_id = move
            rec.state = "released"
            rec.message_post(body=_(
                "Cash advance of %s %s released. Journal entry: %s",
                rec.currency_id.symbol,
                rec.advance_amount,
                rec.release_move_id.name or key,
            ))

    def action_start_liquidation(self):
        self.ensure_one()
        if self.state != "released":
            raise ValidationError(_("Only released advances can enter liquidation."))
        self.write({"state": "in_liquidation"})
        self.message_post(body=_("Liquidation started. Employee is submitting expenses."))

    def action_liquidate(self):
        """Post liquidation. Creates idempotent accounting entry."""
        for rec in self:
            if rec.state != "in_liquidation":
                raise ValidationError(_("Only advances in liquidation can be liquidated."))
            if not rec.line_ids:
                raise ValidationError(_("Cannot liquidate without expense lines."))
            # Check for blocking policy violations
            blocking = rec.policy_exception_ids.filtered(
                lambda v: v.severity == "block" and not v.resolved
            )
            if blocking:
                raise ValidationError(_(
                    "Cannot liquidate: %d blocking policy violation(s) must be resolved first.",
                    len(blocking),
                ))
            key = "CA-LIQUIDATION-%s" % rec.name
            existing = self.env["account.move"].search([("ref", "=", key)], limit=1)
            if existing:
                rec.liquidation_move_id = existing
            else:
                journal = self.env["account.journal"].search(
                    [("type", "=", "general"), ("company_id", "=", rec.company_id.id)],
                    limit=1,
                )
                if not journal:
                    raise ValidationError(_(
                        "No general journal found for company %s.",
                        rec.company_id.name,
                    ))
                move = self.env["account.move"].create({
                    "ref": key,
                    "journal_id": journal.id,
                    "move_type": "entry",
                    "date": fields.Date.context_today(self),
                })
                rec.liquidation_move_id = move
            rec.state = "liquidated"
            rec.finance_posted_by = self.env.user.id
            rec.message_post(body=_(
                "Liquidation posted. Total expenses: %s %s. Settlement: %s %s (%s).",
                rec.currency_id.symbol,
                rec.total_expenses,
                rec.currency_id.symbol,
                abs(rec.settlement_amount),
                rec.settlement_status,
            ))
            # Also update linked cash advance request
            if rec.cash_advance_request_id:
                rec.cash_advance_request_id.action_mark_liquidated()

    def action_close(self):
        self.ensure_one()
        if self.state != "liquidated":
            raise ValidationError(_("Only liquidated advances can be closed."))
        self.write({"state": "closed"})
        self.message_post(body=_("Cash advance closed and fully settled."))
        # Also close linked cash advance request
        if self.cash_advance_request_id and self.cash_advance_request_id.state == "liquidated":
            self.cash_advance_request_id.action_close()

    def action_approve(self):
        """Legacy approve action -- maps to manager_approve for backward compat."""
        return self.action_manager_approve()

    def action_settle(self):
        """Legacy settle -- maps to liquidate for backward compat."""
        return self.action_liquidate()

    def action_reject(self):
        self.ensure_one()
        if self.state not in ("submitted", "manager_approved"):
            raise ValidationError(_("Only submitted or manager-approved requests can be rejected."))
        self.write({"state": "rejected"})
        self.message_post(body=_("Rejected by %s.", self.env.user.name))

    def action_cancel(self):
        self.ensure_one()
        if self.state not in ("draft", "submitted"):
            raise ValidationError(_("Only draft or submitted requests can be cancelled."))
        self.write({"state": "cancelled"})
        self.message_post(body=_("Cancelled by %s.", self.env.user.name))

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state not in ("rejected", "cancelled"):
            raise ValidationError(_("Only rejected or cancelled requests can be reset to draft."))
        self.write({"state": "draft"})
        self.message_post(body=_("Reset to draft."))

    # ── Policy engine ────────────────────────────────────────────────────────

    def action_check_policy(self):
        """Run policy engine against this record and create violation records."""
        for rec in self:
            # Clear previously unresolved violations
            rec.policy_exception_ids.filtered(lambda v: not v.resolved).unlink()
            rules = self.env["hr.expense.policy.rule"].search([
                ("active", "=", True),
                "|", ("company_id", "=", rec.company_id.id),
                     ("company_id", "=", False),
            ])
            for rule in rules:
                if rule.rule_type == "amount_limit" and rule.threshold_amount:
                    if rec.advance_amount > rule.threshold_amount:
                        self.env["hr.expense.policy.violation"].create({
                            "liquidation_id": rec.id,
                            "rule_code": rule.rule_code,
                            "severity": rule.severity,
                            "description": _(
                                "Amount %s exceeds limit of %s.",
                                rec.advance_amount,
                                rule.threshold_amount,
                            ),
                        })
                elif rule.rule_type == "receipt_required" and rule.threshold_amount:
                    for line in rec.line_ids:
                        if line.amount >= rule.threshold_amount and not line.receipt_ids:
                            self.env["hr.expense.policy.violation"].create({
                                "liquidation_id": rec.id,
                                "rule_code": rule.rule_code,
                                "severity": rule.severity,
                                "description": _(
                                    "Line '%s' (%s) requires receipt (threshold: %s).",
                                    line.description,
                                    line.amount,
                                    rule.threshold_amount,
                                ),
                            })
                elif rule.rule_type == "category_limit" and rule.threshold_amount:
                    bucket_totals = {
                        "meals": rec.total_meals,
                        "transportation": rec.total_transportation,
                        "miscellaneous": rec.total_miscellaneous,
                    }
                    for bucket, total in bucket_totals.items():
                        if total > rule.threshold_amount:
                            self.env["hr.expense.policy.violation"].create({
                                "liquidation_id": rec.id,
                                "rule_code": rule.rule_code,
                                "severity": rule.severity,
                                "description": _(
                                    "Category '%s' total %s exceeds limit %s.",
                                    bucket,
                                    total,
                                    rule.threshold_amount,
                                ),
                            })

    # ── Monitoring cron ──────────────────────────────────────────────────────

    @api.model
    def _cron_check_overdue_advances(self):
        """
        Scheduled action: find released advances past the max overdue days
        defined by active OVERDUE_CHECK policy rules and create violations.
        """
        overdue_rules = self.env["hr.expense.policy.rule"].search([
            ("active", "=", True),
            ("rule_type", "=", "overdue_check"),
            ("max_days", ">", 0),
        ])
        if not overdue_rules:
            return
        for rule in overdue_rules:
            cutoff = fields.Date.subtract(fields.Date.today(), days=rule.max_days)
            overdue_records = self.search([
                ("state", "=", "released"),
                ("date", "<=", cutoff),
            ])
            for rec in overdue_records:
                existing = rec.policy_exception_ids.filtered(
                    lambda v: v.rule_code == rule.rule_code and not v.resolved
                )
                if not existing:
                    self.env["hr.expense.policy.violation"].create({
                        "liquidation_id": rec.id,
                        "rule_code": rule.rule_code,
                        "severity": rule.severity,
                        "description": _(
                            "Advance released on %s is overdue by more than %d days.",
                            rec.date,
                            rule.max_days,
                        ),
                    })
                    _logger.info(
                        "Overdue violation created for %s (released %s, rule %s)",
                        rec.name, rec.date, rule.rule_code,
                    )

    # ── Agent integration ────────────────────────────────────────────────────

    def action_trigger_agent_run(self):
        """
        Create an ipai.agent.run targeting this liquidation and open it.
        Requires ipai_agent module to be installed; silently skips if not present.
        """
        self.ensure_one()
        if "ipai.agent.run" not in self.env:
            raise UserError(_("IPAI Agent module is not installed."))
        run = self.env["ipai.agent.run"].find_or_create({
            "tool_id": self._get_default_agent_tool_id(),
            "target_model": self._name,
            "target_res_id": self.id,
            "input_json": __import__("json").dumps({
                "liquidation_name": self.name,
                "employee": self.employee_id.name,
                "total_expenses": self.total_expenses,
                "settlement_amount": self.settlement_amount,
            }),
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "ipai.agent.run",
            "res_id": run.id,
            "view_mode": "form",
            "target": "new",
        }

    def _get_default_agent_tool_id(self):
        """
        Return the ID of the canonical validation tool for liquidation runs.

        Canonical technical name: ``expense_liquidation.validate_and_pack_evidence``
        (seeded by ipai_agent/data/tools_seed.xml on first install).

        If the canonical tool is not present (e.g. ipai_agent not yet installed
        or the seed was not applied), raises a UserError with actionable guidance.
        """
        tool = self.env["ipai.agent.tool"].search([
            ("technical_name", "=", "expense_liquidation.validate_and_pack_evidence"),
            ("active", "=", True),
        ], limit=1)
        if not tool:
            raise UserError(_(
                "No active tool with technical name "
                "'expense_liquidation.validate_and_pack_evidence' found. "
                "Ensure ipai_agent is installed and the module has been upgraded "
                "(IPAI -> Agents -> Configuration -> Tools)."
            ))
        return tool.id

    def action_view_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Expense Lines"),
            "res_model": "hr.expense.liquidation.line",
            "view_mode": "tree,form",
            "domain": [("liquidation_id", "=", self.id)],
            "context": {"default_liquidation_id": self.id},
        }

    def action_view_policy_violations(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Policy Violations"),
            "res_model": "hr.expense.policy.violation",
            "view_mode": "tree,form",
            "domain": [("liquidation_id", "=", self.id)],
            "context": {"default_liquidation_id": self.id},
        }

    def action_view_cash_advance_request(self):
        self.ensure_one()
        if not self.cash_advance_request_id:
            raise UserError(_("No cash advance request linked to this liquidation."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "cash.advance",
            "res_id": self.cash_advance_request_id.id,
            "view_mode": "form",
            "target": "current",
        }


class HrExpenseLiquidationLine(models.Model):
    """
    Individual expense line items with bucket categorization
    and sub-amount columns (Meals, Transport, Misc).
    """

    _name = "hr.expense.liquidation.line"
    _description = "Expense Liquidation Line"
    _order = "date desc, id"

    liquidation_id = fields.Many2one(
        "hr.expense.liquidation",
        string="Liquidation",
        required=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        "res.company",
        related="liquidation_id.company_id",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="liquidation_id.currency_id",
        store=True,
    )

    # Line Details
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
    )
    description = fields.Char(
        string="Description",
        required=True,
    )
    bucket = fields.Selection(
        [
            ("meals", "Meals & Entertainment"),
            ("transportation", "Transportation & Travel"),
            ("miscellaneous", "Miscellaneous"),
        ],
        string="Bucket",
        required=True,
        default="miscellaneous",
        help="Expense category for bucket totals"
    )

    # Sub-amount columns
    meals_amount = fields.Monetary(
        string="Meals",
        currency_field="currency_id",
    )
    transport_amount = fields.Monetary(
        string="Transport",
        currency_field="currency_id",
    )
    misc_amount = fields.Monetary(
        string="Misc",
        currency_field="currency_id",
    )

    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
    )

    # Computed line total from sub-amounts (if provided)
    line_total = fields.Monetary(
        string="Line Total",
        currency_field="currency_id",
        compute="_compute_line_total",
        store=True,
        help="Total of meals + transport + misc sub-amounts, or amount if sub-amounts not used",
    )

    # Client / Cost Element per line
    client_name = fields.Char(string="Client Name")
    ce_number = fields.Char(string="Cost Element")

    # Account
    account_id = fields.Many2one(
        "account.account",
        string="Account",
    )

    # Receipt Attachment
    receipt_ids = fields.Many2many(
        "ir.attachment",
        "expense_line_receipt_rel",
        "line_id",
        "attachment_id",
        string="Receipts",
        help="Attach receipt images/PDFs for this expense line"
    )
    receipt_count = fields.Integer(compute="_compute_receipt_count", string="Receipt Count")

    # Reference
    reference = fields.Char(string="Reference/OR Number")

    # Withholding tax per line (for BIR compliance)
    gross_amount = fields.Monetary(
        string="Gross Amount",
        currency_field="currency_id",
        help="Gross amount before withholding tax",
    )
    withholding_tax_amount = fields.Monetary(
        string="Withholding Tax",
        currency_field="currency_id",
    )
    net_paid_amount = fields.Monetary(
        string="Net Paid",
        currency_field="currency_id",
        help="Net amount after withholding tax deduction",
    )

    # ── Compute methods ──────────────────────────────────────────────────────

    @api.depends("meals_amount", "transport_amount", "misc_amount", "amount")
    def _compute_line_total(self):
        for record in self:
            sub_total = (record.meals_amount or 0.0) + (record.transport_amount or 0.0) + (record.misc_amount or 0.0)
            record.line_total = sub_total if sub_total > 0 else record.amount

    @api.depends("receipt_ids")
    def _compute_receipt_count(self):
        for record in self:
            record.receipt_count = len(record.receipt_ids)

    # ── Onchange ─────────────────────────────────────────────────────────────

    @api.onchange("meals_amount", "transport_amount", "misc_amount")
    def _onchange_sub_amounts(self):
        """Auto-set amount and bucket from sub-amount columns if filled."""
        total = (self.meals_amount or 0.0) + (self.transport_amount or 0.0) + (self.misc_amount or 0.0)
        if total > 0:
            self.amount = total
            # Auto-set bucket based on which sub-amount has value
            if self.meals_amount and not self.transport_amount and not self.misc_amount:
                self.bucket = "meals"
            elif self.transport_amount and not self.meals_amount and not self.misc_amount:
                self.bucket = "transportation"
            elif self.misc_amount and not self.meals_amount and not self.transport_amount:
                self.bucket = "miscellaneous"
            # If multiple sub-amounts are set, keep current bucket

    # ── Actions ──────────────────────────────────────────────────────────────

    def action_view_receipts(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Receipts"),
            "res_model": "ir.attachment",
            "view_mode": "kanban,tree,form",
            "domain": [("id", "in", self.receipt_ids.ids)],
            "context": {"create": False},
        }
