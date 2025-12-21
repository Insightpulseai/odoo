# -*- coding: utf-8 -*-
"""
HR Expense Extension — Expense Approval Events

Emits work items to Master Control when:
- Expense submitted for approval (especially large amounts)
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Default threshold for "large" expenses requiring review
LARGE_EXPENSE_THRESHOLD = 1000.0


class HrExpense(models.Model):
    _name = "hr.expense"
    _inherit = ["hr.expense", "master.control.mixin"]

    # Track if work item was created
    x_master_control_submitted = fields.Boolean(
        string="Work Item Created",
        default=False,
        copy=False,
    )

    def action_submit_expenses(self):
        """Override submit action to emit work item."""
        result = super().action_submit_expenses()

        for expense in self:
            if self._is_event_enabled("expense_submit"):
                expense._emit_expense_work_item()

        return result

    def _emit_expense_work_item(self):
        """Emit expense approval work item to Master Control."""
        self.ensure_one()

        if self.x_master_control_submitted:
            _logger.debug("Expense work item already created for %s", self.name)
            return

        # Determine priority based on amount
        ICP = self.env["ir.config_parameter"].sudo()
        threshold = float(
            ICP.get_param("master_control.expense_threshold", LARGE_EXPENSE_THRESHOLD)
        )

        is_large = self.total_amount >= threshold
        priority = 2 if is_large else 3

        result = self._emit_work_item(
            source="odoo_event",
            source_ref=f"hr.expense:{self.id}:submit",
            title=f"Expense: {self.name} ({self.currency_id.symbol}{self.total_amount:.2f})",
            lane="FIN",
            priority=priority,
            payload={
                "expense_id": self.id,
                "expense_name": self.name,
                "employee_id": self.employee_id.id,
                "employee_name": self.employee_id.name,
                "amount": self.total_amount,
                "currency": self.currency_id.name,
                "is_large_expense": is_large,
                "threshold": threshold,
                "product": self.product_id.name if self.product_id else None,
                "date": str(self.date) if self.date else None,
                "event_type": "expense_approval",
            },
            tags=["expense", "finance", "approval"] + (["large"] if is_large else []),
        )

        if result:
            self.write({"x_master_control_submitted": True})
