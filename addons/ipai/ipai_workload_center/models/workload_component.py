from odoo import fields, models


class IpaiWorkloadComponent(models.Model):
    _name = "ipai.workload.component"
    _description = "Workload Component"
    _rec_name = "name"
    _order = "workload_id, environment_id, name"

    workload_id = fields.Many2one(
        "ipai.workload", required=True, ondelete="cascade"
    )
    environment_id = fields.Many2one(
        "ipai.workload.environment", ondelete="set null"
    )
    name = fields.Char(required=True)
    component_type = fields.Selection(
        [
            ("web", "Web"),
            ("worker", "Worker"),
            ("cron", "Cron"),
            ("db", "Database"),
            ("connector", "Connector"),
            ("pipeline", "Pipeline"),
            ("job", "Job"),
            ("gateway", "Gateway"),
        ],
        required=True,
    )
    runtime_kind = fields.Selection(
        [
            ("odoo", "Odoo"),
            ("aca", "Azure Container App"),
            ("databricks", "Databricks"),
            ("function", "Azure Function"),
            ("github_actions", "GitHub Actions"),
            ("azdo_pipeline", "Azure DevOps Pipeline"),
        ],
    )
    external_ref = fields.Char(help="External resource ID or FQDN")
    status = fields.Selection(
        [
            ("active", "Active"),
            ("stopped", "Stopped"),
            ("degraded", "Degraded"),
            ("unknown", "Unknown"),
        ],
        default="unknown",
    )
    version = fields.Char(help="Image tag or version label")
    metadata_json = fields.Text(help="Arbitrary JSON metadata")
