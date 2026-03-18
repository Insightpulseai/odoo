# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiCloseChecklist(models.Model):
    """Month-end close checklist for PH finance PPM overlay."""

    _name = "ipai.close.checklist"
    _description = "Month-End Close Checklist"
    _order = "period_id desc, sequence"

    name = fields.Char(string="Checklist Name", required=True)
    period_id = fields.Many2one(
        "date.range",
        string="Period",
        domain="[('type_id.name', '=', 'Fiscal Month')]",
        help="The accounting period this checklist belongs to",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    sequence = fields.Integer(default=10)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("blocked", "Blocked"),
        ],
        string="Status",
        default="draft",
    )
    item_ids = fields.One2many(
        "ipai.close.checklist.item",
        "checklist_id",
        string="Checklist Items",
    )
    notes = fields.Text(string="Notes")
    completion_date = fields.Datetime(string="Completion Date")
    assigned_user_id = fields.Many2one(
        "res.users",
        string="Assigned To",
    )

    def action_start(self):
        """Start the checklist."""
        self.write({"state": "in_progress"})

    def action_complete(self):
        """Mark checklist as complete."""
        self.write(
            {
                "state": "completed",
                "completion_date": fields.Datetime.now(),
            }
        )


class IpaiCloseChecklistItem(models.Model):
    """Individual items in a month-end close checklist."""

    _name = "ipai.close.checklist.item"
    _description = "Close Checklist Item"
    _order = "sequence, id"

    checklist_id = fields.Many2one(
        "ipai.close.checklist",
        string="Checklist",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(string="Task", required=True)
    sequence = fields.Integer(default=10)
    is_completed = fields.Boolean(string="Completed", default=False)
    completed_by = fields.Many2one("res.users", string="Completed By")
    completed_date = fields.Datetime(string="Completed Date")
    notes = fields.Text(string="Notes")
    blocking_reason = fields.Text(string="Blocking Reason")

    def action_toggle_complete(self):
        """Toggle completion status."""
        for item in self:
            if item.is_completed:
                item.write(
                    {
                        "is_completed": False,
                        "completed_by": False,
                        "completed_date": False,
                    }
                )
            else:
                item.write(
                    {
                        "is_completed": True,
                        "completed_by": self.env.user.id,
                        "completed_date": fields.Datetime.now(),
                    }
                )
