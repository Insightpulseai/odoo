# -*- coding: utf-8 -*-
from odoo.exceptions import UserError

from odoo import _, api, fields, models


class FinanceSeedWizard(models.TransientModel):
    _name = "ipai.finance.seed.wizard"
    _description = "Seed Finance Framework (Directory + BIR + Templates)"

    strict = fields.Boolean(
        default=False, help="If enabled, invalid rows raise errors."
    )

    def action_seed(self):
        self.ensure_one()
        self.env["ipai.finance.seed.service"].seed_bundle(
            self.env["ipai.finance.seed.service"]._load_bundle_json(),
            strict=self.strict,
        )
        return {"type": "ir.actions.client", "tag": "reload"}
