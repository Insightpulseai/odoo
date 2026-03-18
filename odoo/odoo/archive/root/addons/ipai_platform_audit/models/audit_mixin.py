import json
from datetime import datetime

from odoo import api, fields, models


class AuditMixin(models.AbstractModel):
    """
    Mixin class providing field-level audit trail capabilities.

    Inherit this mixin in your model to gain:
    - Automatic field change logging
    - Change history viewer
    - Configurable audit policies

    Usage:
        class MyModel(models.Model):
            _name = 'my.model'
            _inherit = ['ipai.audit.mixin']

            # Define which fields to audit
            _audit_fields = ['name', 'state', 'amount']
    """

    _name = "ipai.audit.mixin"
    _description = "IPAI Audit Mixin"

    audit_log_ids = fields.One2many(
        "ipai.audit.log",
        "res_id",
        string="Audit Log",
        domain=lambda self: [("res_model", "=", self._name)],
        readonly=True,
    )

    audit_log_count = fields.Integer(
        string="Audit Entries",
        compute="_compute_audit_log_count",
    )

    @api.depends("audit_log_ids")
    def _compute_audit_log_count(self):
        for record in self:
            record.audit_log_count = len(record.audit_log_ids)

    def _get_audit_fields(self):
        """
        Return list of field names to audit.
        Override _audit_fields attribute or this method.
        """
        return getattr(self, "_audit_fields", [])

    def _should_audit_field(self, field_name):
        """Check if a specific field should be audited."""
        audit_fields = self._get_audit_fields()
        if not audit_fields:
            # No explicit list = audit all non-computed fields
            field = self._fields.get(field_name)
            if field:
                return not field.compute and field.store
            return False
        return field_name in audit_fields

    def _log_audit(self, action, field_name=None, old_value=None, new_value=None):
        """
        Create an audit log entry.

        Args:
            action: 'create', 'write', 'unlink', or custom action
            field_name: Name of changed field (for write)
            old_value: Previous value
            new_value: New value
        """
        AuditLog = self.env.get("ipai.audit.log")
        if not AuditLog:
            return

        for record in self:
            AuditLog.sudo().create(
                {
                    "res_model": record._name,
                    "res_id": record.id,
                    "res_name": record.display_name,
                    "action": action,
                    "field_name": field_name,
                    "old_value": str(old_value) if old_value is not None else False,
                    "new_value": str(new_value) if new_value is not None else False,
                    "user_id": self.env.uid,
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to log audit."""
        records = super().create(vals_list)
        for record in records:
            record._log_audit("create")
        return records

    def write(self, vals):
        """Override write to log field changes."""
        # Capture old values for audited fields
        audited_changes = {}
        for record in self:
            old_vals = {}
            for field_name in vals:
                if record._should_audit_field(field_name):
                    old_vals[field_name] = record[field_name]
            if old_vals:
                audited_changes[record.id] = old_vals

        result = super().write(vals)

        # Log changes
        for record in self:
            if record.id in audited_changes:
                old_vals = audited_changes[record.id]
                for field_name, old_value in old_vals.items():
                    new_value = record[field_name]
                    if old_value != new_value:
                        record._log_audit(
                            "write",
                            field_name=field_name,
                            old_value=old_value,
                            new_value=new_value,
                        )

        return result

    def unlink(self):
        """Override unlink to log deletion."""
        for record in self:
            record._log_audit("unlink")
        return super().unlink()

    def action_view_audit_log(self):
        """Action to view audit log for this record."""
        self.ensure_one()
        return {
            "name": f"Audit Log - {self.display_name}",
            "type": "ir.actions.act_window",
            "res_model": "ipai.audit.log",
            "view_mode": "tree,form",
            "domain": [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
            ],
            "context": {"default_res_model": self._name, "default_res_id": self.id},
        }


class AuditLog(models.Model):
    """Audit log entry model."""

    _name = "ipai.audit.log"
    _description = "IPAI Audit Log"
    _order = "create_date desc"
    _rec_name = "display_name"

    res_model = fields.Char(
        string="Model",
        required=True,
        index=True,
    )

    res_id = fields.Integer(
        string="Record ID",
        required=True,
        index=True,
    )

    res_name = fields.Char(
        string="Record Name",
    )

    action = fields.Selection(
        [
            ("create", "Created"),
            ("write", "Updated"),
            ("unlink", "Deleted"),
            ("other", "Other"),
        ],
        string="Action",
        required=True,
    )

    field_name = fields.Char(
        string="Field",
    )

    old_value = fields.Text(
        string="Old Value",
    )

    new_value = fields.Text(
        string="New Value",
    )

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        default=lambda self: self.env.uid,
    )

    display_name = fields.Char(
        compute="_compute_display_name",
    )

    @api.depends("res_model", "res_id", "action", "create_date")
    def _compute_display_name(self):
        for log in self:
            log.display_name = (
                f"{log.res_model}/{log.res_id} - {log.action} - "
                f"{log.create_date.strftime('%Y-%m-%d %H:%M') if log.create_date else ''}"
            )
