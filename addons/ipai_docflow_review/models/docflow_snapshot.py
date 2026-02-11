import json

from odoo import fields, models


class DocflowDocumentSnapshot(models.Model):
    _name = "docflow.document.snapshot"
    _description = "DocFlow Extraction Snapshot"
    _order = "create_date desc"

    document_id = fields.Many2one("docflow.document", required=True, ondelete="cascade")
    source = fields.Selection(
        [("daemon", "Daemon"), ("manual", "Manual"), ("rerun", "Re-run")],
        default="daemon",
    )
    payload_json = fields.Text(required=True)
    diff_text = fields.Text()

    def payload_dict(self):
        try:
            return json.loads(self.payload_json or "{}")
        except Exception:
            return {}
