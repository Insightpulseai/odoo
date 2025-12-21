from odoo import fields, models


class IpaiLocalizationOverlay(models.Model):
    _name = "ipai.localization.overlay"
    _description = "Localization Overlay (PH patches without polluting SAP baseline)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "country, sequence, id"

    country = fields.Selection([("PH", "Philippines")], default="PH", required=True)
    workstream_id = fields.Many2one(
        "ipai.workstream", required=True, ondelete="cascade", index=True
    )
    applies_to_code = fields.Char(
        required=True, help="Task/Check code this overlay applies to"
    )
    patch_type = fields.Selection(
        [
            ("bir_form", "BIR Form"),
            ("deadline", "Deadline Rule"),
            ("evidence", "Evidence Requirement"),
            ("threshold", "Threshold Update"),
            ("odoo_mapping", "Odoo Mapping Patch"),
        ],
        required=True,
    )
    patch_payload = fields.Text(
        required=True,
        help="JSON/YAML-ish payload stored as text (kept simple in scaffold).",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
