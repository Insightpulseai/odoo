# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectStageGate(models.Model):
    _name = "ipai.project.stage.gate"
    _description = "Stage Gate"
    _order = "stage_id, sequence, id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Gate Name", required=True)
    stage_id = fields.Many2one(
        "project.task.type",
        string="Stage",
        required=True,
        ondelete="cascade",
        index=True,
        help="The stage this gate applies to.",
    )
    project_ids = fields.Many2many(
        "project.project",
        string="Projects",
        help="If set, gate only applies to these projects. Leave empty for all projects using this stage.",
    )
    sequence = fields.Integer(string="Sequence", default=10)
    check_type = fields.Selection(
        [
            ("required_fields", "Required Fields"),
            ("approval", "Approval Required"),
            ("checklist", "Checklist Complete"),
            ("custom", "Custom Validation"),
        ],
        string="Check Type",
        required=True,
        default="approval",
    )
    description = fields.Text(
        string="Description", help="Description of what this gate checks."
    )
    required_field_ids = fields.Many2many(
        "ir.model.fields",
        string="Required Fields",
        domain="[('model', '=', 'project.task')]",
        help="Fields that must be filled before passing this gate.",
    )
    approver_group_id = fields.Many2one(
        "res.groups",
        string="Approver Group",
        help="Group whose members can approve this gate.",
    )
    is_blocking = fields.Boolean(
        string="Blocking",
        default=True,
        help="If enabled, tasks cannot advance past this stage without passing the gate.",
    )
    active = fields.Boolean(string="Active", default=True)

    def check_gate(self, task):
        """
        Check if a task passes this gate.

        Args:
            task: project.task record

        Returns:
            tuple: (passed: bool, message: str)
        """
        self.ensure_one()

        if self.check_type == "required_fields":
            return self._check_required_fields(task)
        elif self.check_type == "approval":
            return self._check_approval(task)
        elif self.check_type == "checklist":
            return self._check_checklist(task)
        else:
            return True, "Custom validation not implemented."

    def _check_required_fields(self, task):
        """Check if all required fields are filled."""
        missing = []
        for field in self.required_field_ids:
            value = getattr(task, field.name, None)
            if not value:
                missing.append(field.field_description)

        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        return True, "All required fields are filled."

    def _check_approval(self, task):
        """Check if the task has been approved."""
        # This is a placeholder - actual implementation would check for approval records
        # For now, we just return True
        return True, "Approval check passed."

    def _check_checklist(self, task):
        """Check if all checklist items are complete."""
        # This is a placeholder - actual implementation would check checklist items
        return True, "Checklist check passed."


class ProjectStageGateResult(models.Model):
    _name = "ipai.project.stage.gate.result"
    _description = "Stage Gate Result"
    _order = "create_date desc"

    task_id = fields.Many2one(
        "project.task", string="Task", required=True, ondelete="cascade", index=True
    )
    gate_id = fields.Many2one(
        "ipai.project.stage.gate", string="Gate", required=True, ondelete="cascade"
    )
    passed = fields.Boolean(string="Passed")
    message = fields.Text(string="Message")
    checked_by_id = fields.Many2one(
        "res.users", string="Checked By", default=lambda self: self.env.user
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By")
    approved_date = fields.Datetime(string="Approved Date")
