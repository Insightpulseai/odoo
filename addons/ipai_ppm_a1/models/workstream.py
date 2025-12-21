from odoo import api, fields, models


class IpaiWorkstream(models.Model):
    _name = "ipai.workstream"
    _description = "IPAI Workstream"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    name = fields.Char(required=True, tracking=True)
    code = fields.Selection(
        [("AFC", "AFC - Advanced Financial Closing"), ("STC", "STC - SAP Tax Compliance")],
        required=True,
        default="AFC",
        tracking=True,
    )
    description = fields.Text()
    sap_anchor = fields.Char(help="Canonical SAP taxonomy anchor / doc reference")
    odoo_anchor = fields.Char(help="Odoo mapping anchor (module/model/report refs)")
    active = fields.Boolean(default=True)

    template_ids = fields.One2many("ipai.ppm.template", "workstream_id")
    tasklist_ids = fields.One2many("ipai.ppm.tasklist", "workstream_id")
    check_ids = fields.One2many("ipai.stc.check", "workstream_id")
    scenario_ids = fields.One2many("ipai.stc.scenario", "workstream_id")
    overlay_ids = fields.One2many("ipai.localization.overlay", "workstream_id")

    _sql_constraints = [
        ("workstream_code_unique", "unique(code)", "Workstream code must be unique."),
    ]

    @api.model
    def seed_defaults(self):
        """Idempotent: ensure AFC + STC exist."""
        for code, name in [
            ("AFC", "AFC - Advanced Financial Closing"),
            ("STC", "STC - SAP Tax Compliance"),
        ]:
            ws = self.search([("code", "=", code)], limit=1)
            if not ws:
                self.create({"code": code, "name": name})
        return True
