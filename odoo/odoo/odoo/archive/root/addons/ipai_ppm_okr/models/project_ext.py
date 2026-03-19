from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    ppm_meta_id = fields.One2many("ppm.project.meta", "project_id", string="PPM Meta")
    ppm_portfolio_id = fields.Many2one(
        "ppm.portfolio", compute="_compute_ppm_links", store=False
    )
    ppm_program_id = fields.Many2one(
        "ppm.program", compute="_compute_ppm_links", store=False
    )

    ppm_workstream_ids = fields.One2many("ppm.workstream", "project_id")
    ppm_epic_ids = fields.One2many("ppm.epic", "project_id")
    ppm_risk_ids = fields.One2many("ppm.risk", "project_id")
    ppm_issue_ids = fields.One2many("ppm.issue", "project_id")
    ppm_change_request_ids = fields.One2many("ppm.change.request", "project_id")

    okr_objective_ids = fields.One2many("okr.objective", "project_id")

    def _compute_ppm_links(self):
        for p in self:
            meta = self.env["ppm.project.meta"].search(
                [("project_id", "=", p.id)], limit=1
            )
            p.ppm_portfolio_id = meta.portfolio_id if meta else False
            p.ppm_program_id = meta.program_id if meta else False
