# Copyright (C) InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).
#
# Compatibility shim: defines res.config.settings.anglo_saxon_accounting
# so the Settings form view renders correctly when account_usability (OCA
# account-financial-tools) view XML is stored in the database but the OCA
# module itself is not loadable (not in addons_path at runtime).
#
# This field mirrors what account_usability/models/res_config_settings.py
# defines. If account_usability IS loaded, the last-registered definition
# wins — both point to the same related field on res.company, so there is
# no functional difference.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    anglo_saxon_accounting = fields.Boolean(
        related="company_id.anglo_saxon_accounting",
        readonly=False,
        string="Use Anglo-Saxon Accounting",
        help=(
            "Record the cost of a good as an expense when this good is "
            "invoiced to a final customer (instead of recording the cost "
            "as soon as the product is received in stock)."
        ),
    )
