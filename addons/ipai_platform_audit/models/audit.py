# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models


class IpaiAuditLog(models.Model):
    """Audit log for tracking all changes in IPAI modules."""

    _name = "ipai.audit.log"
    _description = "IPAI Audit Log"
    _order = "create_date desc"

    name = fields.Char(string="Summary", compute="_compute_name", store=True)
    event_type = fields.Selection(
        [
            ("create", "Create"),
            ("write", "Update"),
            ("unlink", "Delete"),
            ("move", "Move"),
            ("share", "Share"),
            ("archive", "Archive"),
            ("restore", "Restore"),
        ],
        string="Event Type",
        required=True,
    )
    model_name = fields.Char(string="Model", required=True, index=True)
    record_id = fields.Integer(string="Record ID", required=True)
    record_name = fields.Char(string="Record Name")
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        default=lambda self: self.env.user,
    )
    old_values = fields.Text(string="Old Values (JSON)")
    new_values = fields.Text(string="New Values (JSON)")
    changes_summary = fields.Text(string="Changes Summary", compute="_compute_changes_summary")

    @api.depends("event_type", "model_name", "record_name")
    def _compute_name(self):
        for record in self:
            record.name = f"{record.event_type}: {record.model_name} - {record.record_name or record.record_id}"

    @api.depends("old_values", "new_values")
    def _compute_changes_summary(self):
        for record in self:
            if not record.old_values and not record.new_values:
                record.changes_summary = ""
                continue

            old = json.loads(record.old_values or "{}")
            new = json.loads(record.new_values or "{}")

            changes = []
            all_keys = set(old.keys()) | set(new.keys())
            for key in sorted(all_keys):
                old_val = old.get(key)
                new_val = new.get(key)
                if old_val != new_val:
                    changes.append(f"{key}: {old_val} -> {new_val}")

            record.changes_summary = "\n".join(changes) if changes else "No changes"

    @api.model
    def log_event(self, event_type, model_name, record_id, record_name=None, old_values=None, new_values=None):
        """Create an audit log entry."""
        return self.create({
            "event_type": event_type,
            "model_name": model_name,
            "record_id": record_id,
            "record_name": record_name,
            "old_values": json.dumps(old_values) if old_values else None,
            "new_values": json.dumps(new_values) if new_values else None,
        })


class IpaiAuditMixin(models.AbstractModel):
    """Mixin to add audit logging to any model."""

    _name = "ipai.audit.mixin"
    _description = "IPAI Audit Mixin"

    def _get_audit_values(self, fields_to_track=None):
        """Get current values for audit logging."""
        self.ensure_one()
        if fields_to_track is None:
            fields_to_track = ["name"]
        return {f: getattr(self, f, None) for f in fields_to_track if hasattr(self, f)}

    @api.model_create_multi
    def create(self, vals_list):
        """Log create events."""
        records = super().create(vals_list)
        audit_log = self.env["ipai.audit.log"]
        for record in records:
            audit_log.log_event(
                event_type="create",
                model_name=self._name,
                record_id=record.id,
                record_name=getattr(record, "name", None) or str(record.id),
                new_values=record._get_audit_values(),
            )
        return records

    def write(self, vals):
        """Log write events."""
        audit_log = self.env["ipai.audit.log"]
        old_values_map = {r.id: r._get_audit_values() for r in self}
        result = super().write(vals)
        for record in self:
            audit_log.log_event(
                event_type="write",
                model_name=self._name,
                record_id=record.id,
                record_name=getattr(record, "name", None) or str(record.id),
                old_values=old_values_map.get(record.id),
                new_values=record._get_audit_values(),
            )
        return result

    def unlink(self):
        """Log unlink events."""
        audit_log = self.env["ipai.audit.log"]
        for record in self:
            audit_log.log_event(
                event_type="unlink",
                model_name=self._name,
                record_id=record.id,
                record_name=getattr(record, "name", None) or str(record.id),
                old_values=record._get_audit_values(),
            )
        return super().unlink()
