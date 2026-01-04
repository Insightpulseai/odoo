# -*- coding: utf-8 -*-
import json
import pkgutil

from odoo.exceptions import UserError

from odoo import _, api, fields, models


class FinanceSeedService(models.Model):
    _name = "ipai.finance.seed.service"
    _description = "Finance Seed Loader (Directory + BIR + Templates)"
    _rec_name = "id"

    @api.model
    def _load_bundle_json(self):
        data = pkgutil.get_data(
            __name__.split(".")[0], "data/seed/finance_framework.seed.json"
        )
        if not data:
            raise UserError(_("Seed bundle not found inside module."))
        try:
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            raise UserError(_("Invalid seed JSON bundle: %s") % (e,))

    @api.model
    def seed_if_empty(self):
        """Seed only when the target tables are empty (safe + idempotent)."""
        Directory = self.env["ipai.finance.directory"]
        Schedule = self.env["ipai.bir.schedule.line"]
        Template = self.env["ipai.finance.task.template"]

        if (
            Directory.search_count([])
            or Schedule.search_count([])
            or Template.search_count([])
        ):
            return False

        bundle = self._load_bundle_json()
        self.seed_bundle(bundle, strict=False)
        return True

    @api.model
    def seed_bundle(self, bundle: dict, strict: bool = False):
        Directory = self.env["ipai.finance.directory"]
        Schedule = self.env["ipai.bir.schedule.line"]
        Template = self.env["ipai.finance.task.template"]

        directory = bundle.get("directory", [])
        bir_schedule = bundle.get("bir_schedule", [])
        templates = bundle.get("task_templates", [])

        # Directory
        for row in directory:
            Directory._upsert_from_seed(row, strict=strict)

        # Templates
        for row in templates:
            Template._upsert_from_seed(row, strict=strict)

        # Schedule
        for row in bir_schedule:
            Schedule._upsert_from_seed(row, strict=strict)

        return True
