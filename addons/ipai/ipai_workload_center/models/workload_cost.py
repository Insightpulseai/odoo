from odoo import fields, models


class IpaiWorkloadCostSnapshot(models.Model):
    _name = "ipai.workload.cost.snapshot"
    _description = "Workload Cost Snapshot"
    _rec_name = "display_name"
    _order = "captured_on desc"

    workload_id = fields.Many2one(
        "ipai.workload", required=True, ondelete="cascade"
    )
    environment_id = fields.Many2one(
        "ipai.workload.environment", ondelete="set null"
    )
    captured_on = fields.Date(required=True)
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )
    cost_amount = fields.Monetary(currency_field="currency_id")
    source = fields.Char(help="e.g. azure-cost-management, manual")
    details_json = fields.Text(help="Breakdown by resource group, service, etc.")

    display_name = fields.Char(compute="_compute_display_name", store=True)

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"{rec.workload_id.key or ''} / {rec.captured_on or ''}"
            )
