# -*- coding: utf-8 -*-
"""
Purchase Order Extension — Large Purchase Events

Emits work items to Master Control when:
- Purchase order confirmed above threshold
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Default threshold for "large" purchases requiring review
LARGE_PURCHASE_THRESHOLD = 5000.0


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "master.control.mixin"]

    # Track if work item was created
    x_master_control_submitted = fields.Boolean(
        string="Work Item Created",
        default=False,
        copy=False,
    )

    def button_confirm(self):
        """Override confirm to emit work item for large purchases."""
        result = super().button_confirm()

        for order in self:
            if self._is_event_enabled("purchase_large"):
                order._check_and_emit_purchase_work_item()

        return result

    def _check_and_emit_purchase_work_item(self):
        """Emit purchase review work item if above threshold."""
        self.ensure_one()

        if self.x_master_control_submitted:
            _logger.debug("Purchase work item already created for %s", self.name)
            return

        ICP = self.env["ir.config_parameter"].sudo()
        threshold = float(
            ICP.get_param("master_control.purchase_threshold", LARGE_PURCHASE_THRESHOLD)
        )

        if self.amount_total < threshold:
            _logger.debug(
                "Purchase %s below threshold (%.2f < %.2f), skipping",
                self.name,
                self.amount_total,
                threshold,
            )
            return

        result = self._emit_work_item(
            source="odoo_event",
            source_ref=f"purchase.order:{self.id}:confirm",
            title=f"Large PO: {self.name} ({self.currency_id.symbol}{self.amount_total:.2f})",
            lane="FIN",
            priority=2,
            payload={
                "purchase_id": self.id,
                "purchase_name": self.name,
                "partner_id": self.partner_id.id,
                "partner_name": self.partner_id.name,
                "amount": self.amount_total,
                "currency": self.currency_id.name,
                "threshold": threshold,
                "order_date": str(self.date_order) if self.date_order else None,
                "user_id": self.user_id.id if self.user_id else None,
                "user_name": self.user_id.name if self.user_id else None,
                "line_count": len(self.order_line),
                "event_type": "purchase_review",
            },
            tags=["purchase", "finance", "large", "review"],
        )

        if result:
            self.write({"x_master_control_submitted": True})
