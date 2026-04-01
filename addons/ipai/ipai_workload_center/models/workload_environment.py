from odoo import _, api, fields, models


class IpaiWorkloadEnvironment(models.Model):
    _name = "ipai.workload.environment"
    _description = "Workload Environment"
    _inherit = ["mail.thread"]
    _rec_name = "display_name"
    _order = "workload_id, name"

    workload_id = fields.Many2one(
        "ipai.workload", required=True, ondelete="cascade", tracking=True
    )
    name = fields.Char(required=True, tracking=True, help="e.g. dev, staging, prod")
    environment_type = fields.Selection(
        [
            ("dev", "Development"),
            ("staging", "Staging"),
            ("prod", "Production"),
        ],
        required=True,
        tracking=True,
    )
    url = fields.Char(help="Primary endpoint URL")
    health_status = fields.Selection(
        [
            ("unknown", "Unknown"),
            ("healthy", "Healthy"),
            ("degraded", "Degraded"),
            ("down", "Down"),
        ],
        default="unknown",
        tracking=True,
    )
    cost_status = fields.Char(help="Last known cost summary")
    release_id_current = fields.Many2one(
        "ipai.workload.release", string="Current Release"
    )
    topology_snapshot_json = fields.Text(help="JSON snapshot of environment topology")
    last_sync_at = fields.Datetime()

    display_name = fields.Char(compute="_compute_display_name", store=True)

    component_ids = fields.One2many(
        "ipai.workload.component", "environment_id", string="Components"
    )

    @api.depends("workload_id.name", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.workload_id.name or ''} / {rec.name or ''}"
