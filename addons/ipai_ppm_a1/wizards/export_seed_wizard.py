from odoo import fields, models


class IpaiExportSeedWizard(models.TransientModel):
    _name = "ipai.export.seed.wizard"
    _description = "Export Seed Data (JSON)"

    export_path = fields.Char(help="Optional: server filesystem path (writes JSON).")
    webhook_url = fields.Char(help="Optional: POST JSON to webhook (n8n/CI).")

    def action_export(self):
        """Create export run and optionally write to path/webhook."""
        self.ensure_one()
        run = (
            self.env["ipai.repo.export_run"]
            .sudo()
            .create(
                {
                    "name": "Seed Export",
                    "export_path": self.export_path,
                    "webhook_url": self.webhook_url,
                }
            )
        )
        run.action_generate_payload()
        if self.export_path:
            run.action_write_to_path()
        if self.webhook_url:
            run.action_post_webhook()

        return {
            "type": "ir.actions.act_window",
            "name": "Export Run",
            "res_model": "ipai.repo.export_run",
            "view_mode": "form",
            "res_id": run.id,
            "target": "current",
        }
