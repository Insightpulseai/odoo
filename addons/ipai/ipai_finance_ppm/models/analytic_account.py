from odoo import api, fields, models

class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    ipai_ppm_budget_amount = fields.Monetary(
        string="PPM Budget",
        currency_field="currency_id",
        tracking=True,
    )
    ipai_ppm_budget_source_project_id = fields.Many2one(
        "project.project",
        string="Budget Source Project",
        index=True,
        readonly=True,
    )
    ipai_ppm_import_batch_id = fields.Char(string="Import Batch ID", index=True, readonly=True)
    ipai_ppm_imported_at = fields.Datetime(string="Imported At", readonly=True)
    ipai_ppm_import_source = fields.Char(string="Import Source", readonly=True)

    @api.model
    def ipai_sync_project_budget_to_analytic(self, project_id):
        p = self.env["project.project"].browse(project_id)
        if not p.exists():
            return False
        aa = p.analytic_account_id
        if not aa:
            return False
        aa.write({
            "ipai_ppm_budget_amount": p.ipai_ppm_budget_amount,
            "ipai_ppm_budget_source_project_id": p.id,
        })
        return True
