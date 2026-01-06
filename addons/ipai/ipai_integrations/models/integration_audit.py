# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IntegrationAudit(models.Model):
    """Audit log for integration activities."""

    _name = "ipai.integration.audit"
    _description = "Integration Audit Log"
    _order = "create_date desc"
    _log_access = True

    connector_id = fields.Many2one(
        "ipai.integration.connector",
        ondelete="set null",
        index=True
    )
    connector_type = fields.Selection(
        related="connector_id.connector_type",
        store=True
    )

    action = fields.Char(required=True, index=True)
    message = fields.Text()

    level = fields.Selection([
        ("debug", "Debug"),
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
    ], default="info", index=True)

    # Request/response details
    request_method = fields.Char()
    request_url = fields.Char()
    request_payload = fields.Text()
    response_code = fields.Integer()
    response_body = fields.Text()

    # Duration
    duration_ms = fields.Integer(help="Request duration in milliseconds")

    # User context
    user_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        index=True
    )
    ip_address = fields.Char()

    @api.model
    def log(self, connector_id, action, message, level="info", **kwargs):
        """Convenience method to create audit log entries."""
        vals = {
            "connector_id": connector_id,
            "action": action,
            "message": message,
            "level": level,
        }
        vals.update(kwargs)
        return self.create(vals)

    @api.autovacuum
    def _gc_old_logs(self):
        """Clean up old audit logs (keep 90 days)."""
        limit_date = fields.Datetime.subtract(
            fields.Datetime.now(),
            days=90
        )
        old_logs = self.search([
            ("create_date", "<", limit_date),
            ("level", "in", ["debug", "info"]),
        ])
        old_logs.unlink()
