# -*- coding: utf-8 -*-
"""
HR Employee Extension — Onboarding/Offboarding Events

Emits work items to Master Control when:
- New employee created (onboarding)
- Employee departure_date set (offboarding)
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ["hr.employee", "master.control.mixin"]

    # Track if onboarding work item was created
    x_master_control_onboarded = fields.Boolean(
        string="Onboarding Work Item Created",
        default=False,
        copy=False,
    )

    # Track if offboarding work item was created
    x_master_control_offboarded = fields.Boolean(
        string="Offboarding Work Item Created",
        default=False,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Create employee and emit onboarding work item."""
        records = super().create(vals_list)

        for employee in records:
            if self._is_event_enabled("employee_hire"):
                employee._emit_onboarding_work_item()

        return records

    def write(self, vals):
        """Watch for departure_date changes."""
        result = super().write(vals)

        if "departure_date" in vals and vals["departure_date"]:
            for employee in self:
                if (
                    self._is_event_enabled("employee_departure")
                    and not employee.x_master_control_offboarded
                ):
                    employee._emit_offboarding_work_item()

        return result

    def _emit_onboarding_work_item(self):
        """Emit onboarding work item to Master Control."""
        self.ensure_one()

        if self.x_master_control_onboarded:
            _logger.debug("Onboarding work item already created for %s", self.name)
            return

        result = self._emit_work_item(
            source="odoo_event",
            source_ref=f"hr.employee:{self.id}:hire",
            title=f"Onboard: {self.name} ({self.department_id.name or 'No Dept'})",
            lane="HR",
            priority=2,
            payload={
                "employee_id": self.id,
                "employee_name": self.name,
                "department_id": self.department_id.id if self.department_id else None,
                "department_name": (
                    self.department_id.name if self.department_id else None
                ),
                "job_title": self.job_title or "",
                "manager_id": self.parent_id.id if self.parent_id else None,
                "manager_name": self.parent_id.name if self.parent_id else None,
                "work_email": self.work_email or "",
                "event_type": "onboarding",
            },
            tags=["onboarding", "hr"],
        )

        if result:
            self.write({"x_master_control_onboarded": True})

    def _emit_offboarding_work_item(self):
        """Emit offboarding work item to Master Control."""
        self.ensure_one()

        if self.x_master_control_offboarded:
            _logger.debug("Offboarding work item already created for %s", self.name)
            return

        result = self._emit_work_item(
            source="odoo_event",
            source_ref=f"hr.employee:{self.id}:departure",
            title=f"Offboard: {self.name} ({self.department_id.name or 'No Dept'})",
            lane="HR",
            priority=2,
            payload={
                "employee_id": self.id,
                "employee_name": self.name,
                "department_id": self.department_id.id if self.department_id else None,
                "department_name": (
                    self.department_id.name if self.department_id else None
                ),
                "departure_date": (
                    str(self.departure_date) if self.departure_date else None
                ),
                "departure_reason": (
                    self.departure_reason_id.name if self.departure_reason_id else None
                ),
                "manager_id": self.parent_id.id if self.parent_id else None,
                "manager_name": self.parent_id.name if self.parent_id else None,
                "event_type": "offboarding",
            },
            tags=["offboarding", "hr"],
        )

        if result:
            self.write({"x_master_control_offboarded": True})

    def action_trigger_onboarding(self):
        """Manual action to trigger onboarding work item."""
        for employee in self:
            employee.x_master_control_onboarded = False
            employee._emit_onboarding_work_item()
        return True

    def action_trigger_offboarding(self):
        """Manual action to trigger offboarding work item."""
        for employee in self:
            employee.x_master_control_offboarded = False
            employee._emit_offboarding_work_item()
        return True
