import base64
import csv
import io
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class IpaipPmImportWizard(models.TransientModel):
    _name = "ipai.ppm.import.wizard"
    _description = "PPM Import Wizard (deterministic CSV)"

    file = fields.Binary(required=True)
    filename = fields.Char()
    source = fields.Char(default="csv")
    batch_id = fields.Char(default=lambda self: fields.Datetime.now().strftime("%Y%m%d%H%M%S"))

    def action_import(self):
        self.ensure_one()
        data = base64.b64decode(self.file or b"")
        f = io.StringIO(data.decode("utf-8"))
        reader = csv.DictReader(f)

        # Required columns (clarity)
        required = {"project_name", "budget_amount", "cost_center"}
        if not required.issubset(set(reader.fieldnames or [])):
            missing = sorted(required - set(reader.fieldnames or []))
            raise UserError(_("Missing required CSV columns: %s", ", ".join(missing)))

        Project = self.env["project.project"]
        for row in reader:
            name = row["project_name"].strip()
            budget = float(row["budget_amount"] or 0)
            cc = row["cost_center"].strip()

            proj = Project.search([("name", "=", name)], limit=1)
            if not proj:
                proj = Project.create({"name": name})

            proj.write({
                "ipai_ppm_budget_amount": budget,
                "ipai_ppm_cost_center": cc,
            })
            proj.ipai_apply_import_provenance([proj.id], self.batch_id, self.source)
            self.env["account.analytic.account"].ipai_sync_project_budget_to_analytic(proj.id)

        return {"type": "ir.actions.act_window_close"}
