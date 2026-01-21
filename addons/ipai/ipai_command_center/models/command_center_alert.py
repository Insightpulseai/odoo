from odoo import models, fields, api


class CommandCenterAlert(models.Model):
    _name = "ipai.command.center.alert"
    _description = "Command Center Alert"
    _order = "create_date desc"

    name = fields.Char(string="Alert", required=True)
    alert_type = fields.Selection(
        [
            ("info", "Info"),
            ("warning", "Warning"),
            ("error", "Error"),
            ("critical", "Critical"),
        ],
        string="Type",
        default="info",
        required=True,
    )
    state = fields.Selection(
        [
            ("active", "Active"),
            ("acknowledged", "Acknowledged"),
            ("resolved", "Resolved"),
        ],
        string="State",
        default="active",
        required=True,
    )

    message = fields.Text(string="Message")
    source_model = fields.Char(string="Source Model")
    source_res_id = fields.Integer(string="Source Record ID")

    # Timing
    acknowledged_date = fields.Datetime(string="Acknowledged At")
    acknowledged_by = fields.Many2one("res.users", string="Acknowledged By")
    resolved_date = fields.Datetime(string="Resolved At")
    resolved_by = fields.Many2one("res.users", string="Resolved By")

    # Relations
    run_id = fields.Many2one(
        "ipai.command.center.run",
        string="Related Run",
        ondelete="set null",
    )
    user_id = fields.Many2one(
        "res.users",
        string="Assigned To",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    def action_acknowledge(self):
        """Acknowledge the alert."""
        self.write(
            {
                "state": "acknowledged",
                "acknowledged_date": fields.Datetime.now(),
                "acknowledged_by": self.env.user.id,
            }
        )

    def action_resolve(self):
        """Mark alert as resolved."""
        self.write(
            {
                "state": "resolved",
                "resolved_date": fields.Datetime.now(),
                "resolved_by": self.env.user.id,
            }
        )

    @api.model
    def create_alert(self, name, alert_type="warning", message=None, run_id=None):
        """Utility method to create alerts from code."""
        return self.create(
            {
                "name": name,
                "alert_type": alert_type,
                "message": message,
                "run_id": run_id,
            }
        )

    @api.model
    def get_active_alerts_count(self):
        """Get count of active alerts by type."""
        result = {}
        for alert_type, _ in self._fields["alert_type"].selection:
            result[alert_type] = self.search_count(
                [
                    ("state", "=", "active"),
                    ("alert_type", "=", alert_type),
                ]
            )
        return result
