from odoo import api, fields, models

class ProjectProject(models.Model):
    _inherit = "project.project"

    ipai_ppm_budget_amount = fields.Monetary(
        string="PPM Budget",
        currency_field="company_currency_id",
        tracking=True,
    )
    ipai_ppm_budget_currency_id = fields.Many2one(
        "res.currency",
        string="Budget Currency",
        default=lambda self: self.env.company.currency_id.id,
    )
    ipai_ppm_cost_center = fields.Char(string="Cost Center", tracking=True)
    ipai_ppm_import_batch_id = fields.Char(string="Import Batch ID", index=True, readonly=True)
    ipai_ppm_imported_at = fields.Datetime(string="Imported At", readonly=True)
    ipai_ppm_import_source = fields.Char(string="Import Source", readonly=True)

    company_currency_id = fields.Many2one(related="company_id.currency_id", store=False, readonly=True)

    @api.model
    def ipai_apply_import_provenance(self, project_ids, batch_id, source):
        projects = self.browse(project_ids)
        now = fields.Datetime.now()
        projects.write({
            "ipai_ppm_import_batch_id": batch_id,
            "ipai_ppm_imported_at": now,
            "ipai_ppm_import_source": source,
        })
        return True
