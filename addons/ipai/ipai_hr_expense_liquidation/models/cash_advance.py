# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CashAdvance(models.Model):
    """
    Cash Advance Request Model

    Pre-spend request form for employees to request cash advances
    before travel or events. Separate from the liquidation (post-spend).

    Workflow:
        draft -> submitted -> dept_approved -> finance_approved
        -> released -> for_liquidation -> liquidated -> closed
        Plus: rejected, cancelled
    """

    _name = "cash.advance"
    _description = "Cash Advance Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_needed desc, id desc"

    # ── Field declarations ──────────────────────────────────────────────────

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        default=lambda self: _("New"),
        copy=False,
        index=True,
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

    # Payee
    payee_name = fields.Char(
        string="Payee Name",
        help="Name of the person who receives the cash advance",
    )

    # Dates
    date_needed = fields.Date(
        string="Date Needed",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    travel_event_date_from = fields.Date(string="Travel/Event Start")
    travel_event_date_to = fields.Date(string="Travel/Event End")

    # Payment
    payment_method = fields.Selection(
        [
            ("check", "Check"),
            ("autocredit", "Auto-Credit"),
            ("online_transfer", "Online Transfer"),
        ],
        string="Payment Method",
        default="online_transfer",
        required=True,
        tracking=True,
    )

    # Purpose Lines
    purpose_line_ids = fields.One2many(
        "cash.advance.line",
        "cash_advance_id",
        string="Purpose / Breakdown",
        copy=True,
    )

    # Client
    is_client_related = fields.Boolean(
        string="Client Related",
        default=False,
    )
    client_name = fields.Char(string="Client Name")
    ce_number = fields.Char(string="Cost Element Number")

    # Branch
    branch_id = fields.Many2one(
        "operating.branch",
        string="Branch",
    )

    # Currency
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    # Totals
    total_amount = fields.Monetary(
        string="Total Amount",
        currency_field="currency_id",
        compute="_compute_total_amount",
        store=True,
    )

    # State
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("dept_approved", "Dept. Approved"),
            ("finance_approved", "Finance Approved"),
            ("released", "Released"),
            ("for_liquidation", "For Liquidation"),
            ("liquidated", "Liquidated"),
            ("closed", "Closed"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    # Approval
    approver_id = fields.Many2one(
        "res.users",
        string="Department Approver",
        readonly=True,
        tracking=True,
    )
    approval_date = fields.Datetime(
        string="Department Approval Date",
        readonly=True,
    )
    finance_approver_id = fields.Many2one(
        "res.users",
        string="Finance Approver",
        readonly=True,
        tracking=True,
    )
    finance_approval_date = fields.Datetime(
        string="Finance Approval Date",
        readonly=True,
    )

    # Liquidation link
    liquidation_id = fields.Many2one(
        "hr.expense.liquidation",
        string="Liquidation",
        readonly=True,
        copy=False,
    )
    liquidation_due_date = fields.Date(
        string="Liquidation Due Date",
        readonly=True,
        help="Auto-set on release: travel/event end date + 15 calendar days",
    )

    # Calendar
    calendar_event_id = fields.Many2one(
        "calendar.event",
        string="Calendar Event",
        readonly=True,
        copy=False,
    )

    # Overdue
    is_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_is_overdue",
        store=True,
    )

    # Notes
    notes = fields.Text(string="Internal Notes")
    description = fields.Text(string="Purpose")

    # ── SQL constraints ─────────────────────────────────────────────────────

    _sql_constraints = [
        ("name_uniq", "unique(name)", "Cash Advance reference must be unique!"),
    ]

    # ── Compute methods ─────────────────────────────────────────────────────

    @api.depends("purpose_line_ids.amount")
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.purpose_line_ids.mapped("amount"))

    @api.depends("liquidation_due_date", "state")
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for rec in self:
            if (
                rec.liquidation_due_date
                and rec.state in ("released", "for_liquidation")
                and rec.liquidation_due_date < today
            ):
                rec.is_overdue = True
            else:
                rec.is_overdue = False

    # ── Constraints ─────────────────────────────────────────────────────────

    @api.constrains("travel_event_date_from", "travel_event_date_to")
    def _check_travel_dates(self):
        for rec in self:
            if rec.travel_event_date_from and rec.travel_event_date_to:
                if rec.travel_event_date_from > rec.travel_event_date_to:
                    raise ValidationError(
                        _("Travel/Event start date must be before end date.")
                    )

    # ── CRUD overrides ──────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("cash.advance")
                    or _("New")
                )
        return super().create(vals_list)

    # ── State transitions ───────────────────────────────────────────────────

    def action_submit(self):
        self.ensure_one()
        if not self.purpose_line_ids:
            raise ValidationError(
                _("Cannot submit without at least one purpose/breakdown line.")
            )
        if self.total_amount <= 0:
            raise ValidationError(
                _("Total amount must be greater than zero.")
            )
        self.write({"state": "submitted"})
        self.message_post(body=_("Cash advance request submitted for approval."))

    def action_dept_approve(self):
        self.ensure_one()
        if self.state != "submitted":
            raise ValidationError(
                _("Only submitted requests can be department-approved.")
            )
        self.write({
            "state": "dept_approved",
            "approver_id": self.env.user.id,
            "approval_date": fields.Datetime.now(),
        })
        self.message_post(
            body=_("Department approved by %s.", self.env.user.name)
        )

    def action_finance_approve(self):
        self.ensure_one()
        if self.state != "dept_approved":
            raise ValidationError(
                _("Only department-approved requests can be finance-approved.")
            )
        self.write({
            "state": "finance_approved",
            "finance_approver_id": self.env.user.id,
            "finance_approval_date": fields.Datetime.now(),
        })
        self.message_post(
            body=_("Finance approved by %s.", self.env.user.name)
        )

    def action_release(self):
        """Release cash advance. Sets liquidation due date and optionally creates calendar event."""
        self.ensure_one()
        if self.state != "finance_approved":
            raise ValidationError(
                _("Only finance-approved requests can be released.")
            )
        # Calculate liquidation due date: event end + 15 days (or date_needed + 15 if no event)
        base_date = self.travel_event_date_to or self.date_needed
        due_date = base_date + timedelta(days=15)

        vals = {
            "state": "released",
            "liquidation_due_date": due_date,
        }

        # Create calendar event for the due date
        if not self.calendar_event_id:
            event = self.env["calendar.event"].create({
                "name": _("Liquidation Due: %s", self.name),
                "start": fields.Datetime.to_datetime(due_date),
                "stop": fields.Datetime.to_datetime(due_date),
                "allday": True,
                "user_id": self.employee_id.user_id.id or self.env.user.id,
                "description": _(
                    "Cash advance %s liquidation is due.\n"
                    "Employee: %s\nAmount: %s %s",
                    self.name,
                    self.employee_id.name,
                    self.currency_id.symbol,
                    self.total_amount,
                ),
            })
            vals["calendar_event_id"] = event.id

        self.write(vals)
        self.message_post(
            body=_(
                "Cash advance of %s %s released. Liquidation due by %s.",
                self.currency_id.symbol,
                self.total_amount,
                due_date,
            )
        )

    def action_start_liquidation(self):
        """Create linked liquidation record and transition to for_liquidation."""
        self.ensure_one()
        if self.state != "released":
            raise ValidationError(
                _("Only released advances can start liquidation.")
            )
        # Create the linked liquidation record
        liquidation = self.env["hr.expense.liquidation"].create({
            "liquidation_type": "cash_advance",
            "employee_id": self.employee_id.id,
            "company_id": self.company_id.id,
            "advance_amount": self.total_amount,
            "advance_reference": self.name,
            "advance_date": self.date_needed,
            "description": self.description,
            "cash_advance_request_id": self.id,
            "branch_id": self.branch_id.id if self.branch_id else False,
            "client_name": self.client_name,
            "ce_number": self.ce_number,
        })
        self.write({
            "state": "for_liquidation",
            "liquidation_id": liquidation.id,
        })
        self.message_post(
            body=_(
                "Liquidation %s created. Employee is submitting expenses.",
                liquidation.name,
            )
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.expense.liquidation",
            "res_id": liquidation.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_mark_liquidated(self):
        self.ensure_one()
        if self.state != "for_liquidation":
            raise ValidationError(
                _("Only advances in liquidation can be marked as liquidated.")
            )
        self.write({"state": "liquidated"})
        self.message_post(body=_("Cash advance marked as liquidated."))

    def action_close(self):
        self.ensure_one()
        if self.state != "liquidated":
            raise ValidationError(
                _("Only liquidated advances can be closed.")
            )
        self.write({"state": "closed"})
        self.message_post(body=_("Cash advance closed and fully settled."))

    def action_reject(self):
        self.ensure_one()
        if self.state not in ("submitted", "dept_approved"):
            raise ValidationError(
                _("Only submitted or department-approved requests can be rejected.")
            )
        self.write({"state": "rejected"})
        self.message_post(body=_("Rejected by %s.", self.env.user.name))

    def action_cancel(self):
        self.ensure_one()
        if self.state not in ("draft", "submitted"):
            raise ValidationError(
                _("Only draft or submitted requests can be cancelled.")
            )
        self.write({"state": "cancelled"})
        self.message_post(body=_("Cancelled by %s.", self.env.user.name))

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state not in ("rejected", "cancelled"):
            raise ValidationError(
                _("Only rejected or cancelled requests can be reset to draft.")
            )
        self.write({"state": "draft"})
        self.message_post(body=_("Reset to draft."))

    # ── Business methods ────────────────────────────────────────────────────

    def action_view_liquidation(self):
        self.ensure_one()
        if not self.liquidation_id:
            raise UserError(_("No liquidation linked to this cash advance."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.expense.liquidation",
            "res_id": self.liquidation_id.id,
            "view_mode": "form",
            "target": "current",
        }
